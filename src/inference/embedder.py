import numpy as np
import torch

from src.core.models.encoders.audio_encoder import SimpleAudioEncoder
from src.core.models.encoders.image_encoder import SimpleImageEncoder
from src.training.scripts.train_768_128k_scaffold import ScaffoldConfig, SimpleTransformerModel
from src.training.tokenizer.simple_tokenizer import SimpleTokenizer


class UnifiedEmbedder:
    def __init__(self, ckpt_path=None, device='cuda'):
        self.device = device
        self.text_cfg = ScaffoldConfig()
        self.text_cfg.device = device
        self.tokenizer = SimpleTokenizer()
        if ckpt_path is not None:
            ckpt = torch.load(str(ckpt_path), map_location=device, weights_only=True)
            cfg = ckpt.get('cfg', {}) if isinstance(ckpt, dict) else {}
            self.text_cfg.embed_dim = cfg.get('embed_dim', self.text_cfg.embed_dim)
            self.text_cfg.num_layers = cfg.get('num_layers', self.text_cfg.num_layers)
            self.text_cfg.num_heads = cfg.get('num_heads', self.text_cfg.num_heads)
            self.text_cfg.ff_dim = cfg.get('ff_dim', self.text_cfg.ff_dim)
            self.text_cfg.vocab_size = cfg.get('vocab_size', self.text_cfg.vocab_size)
            self.text_cfg.attn_type = cfg.get('attn_type', self.text_cfg.attn_type)
        self.text_model = SimpleTransformerModel(self.text_cfg).to(device)
        if ckpt_path is not None and isinstance(ckpt, dict) and 'model_state_dict' in ckpt:
            st = ckpt['model_state_dict']
            st = {k.replace('module.',''):v for k,v in st.items()}
            self.text_model.load_state_dict(st, strict=False)
        self.image_enc = SimpleImageEncoder(out_dim=self.text_cfg.embed_dim).to(device)
        self.audio_enc = SimpleAudioEncoder(out_dim=self.text_cfg.embed_dim).to(device)
        # fusion projection
        self.fusion = torch.nn.Linear(self.text_cfg.embed_dim * 3, self.text_cfg.embed_dim).to(device)

    def embed_text_long(self, text, seq_len=512):
        # chunk text into seq_len windows and compute per-chunk pooled embeddings, then mean-pool
        ids = self.tokenizer.encode(text, seq_len)
        # if text shorter than seq_len, simple
        if sum(1 for x in ids if x!=0) <= seq_len:
            inp = torch.tensor([ids], dtype=torch.long, device=self.device)
            with torch.no_grad():
                self.text_model(inp)
                # pool the last hidden layer
                hidden = self.text_model.ln(self.text_model.token_emb(inp) + self.text_model.pos_emb(inp.shape[1]).unsqueeze(0).to(self.device))
                mask = (inp != 0).to(torch.float32).unsqueeze(-1)
                pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-6)
                return pooled.cpu().numpy()[0]
        # for long inputs, naive chunking by sliding window
        chunks = []
        text_chars = text
        i = 0
        while i < len(text_chars):
            chunk = text_chars[i:i+seq_len]
            ids = self.tokenizer.encode(chunk, seq_len)
            chunks.append(ids)
            i += seq_len
        embs = []
        for c in chunks:
            inp = torch.tensor([c], dtype=torch.long, device=self.device)
            with torch.no_grad():
                hidden = self.text_model.ln(self.text_model.token_emb(inp) + self.text_model.pos_emb(inp.shape[1]).unsqueeze(0).to(self.device))
                mask = (inp != 0).to(torch.float32).unsqueeze(-1)
                pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-6)
                embs.append(pooled.cpu().numpy()[0])
        embs = np.stack(embs, axis=0)
        # aggregate chunks
        return embs.mean(axis=0)

    def embed_image(self, img_path):
        with torch.no_grad():
            out = self.image_enc(img_path, device=self.device)
            return out.cpu().numpy()[0]

    def embed_audio(self, waveform_np):
        wt = torch.tensor(waveform_np, dtype=torch.float32, device=self.device)
        with torch.no_grad():
            out = self.audio_enc(wt)
            return out.cpu().numpy()[0]

    def embed_unified(self, text=None, img_path=None, audio_waveform=None):
        t = self.embed_text_long(text or '') if text is not None else np.zeros((self.text_cfg.embed_dim,))
        i = self.embed_image(img_path) if img_path is not None else np.zeros((self.text_cfg.embed_dim,))
        a = self.embed_audio(audio_waveform) if audio_waveform is not None else np.zeros((self.text_cfg.embed_dim,))
        comb = np.concatenate([t,i,a], axis=0)
        comb_t = torch.tensor(comb, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            fused = self.fusion(comb_t).cpu().numpy()[0]
        return fused
