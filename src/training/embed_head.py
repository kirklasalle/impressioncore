import torch
import torch.nn as nn


class EmbeddingReconstructionHead(nn.Module):
    """Simple MLP head that takes precomputed embeddings and learns a reconstruction/transform.
    Useful as a small training target to ensure embeddings and training pipeline work.
    """
    def __init__(self, dim: int = 768, hidden: int = 1024):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, hidden),
            nn.GELU(),
            nn.Linear(hidden, dim),
        )

    def forward(self, x):
        return self.net(x)


class EmbeddingReconstructionHeadV2(nn.Module):
        """Enhanced head with LayerNorm + (optional) Dropout and final LayerNorm.

        Architecture (if final_norm=True):
            Linear -> GELU -> LayerNorm(hidden) -> Dropout(p) -> Linear -> LayerNorm(dim)

        If final_norm is False the last LayerNorm is omitted, which can help when
        the additional variance suppression slows convergence relative to a simpler
        baseline (observed in some adaptation runs).
        """
        def __init__(self, dim: int = 768, hidden: int = 1024, dropout: float = 0.05, final_norm: bool = True):
                super().__init__()
                self.fc1 = nn.Linear(dim, hidden)
                self.act = nn.GELU()
                self.ln_hidden = nn.LayerNorm(hidden)
                self.do = nn.Dropout(dropout) if dropout and dropout > 0 else nn.Identity()
                self.fc2 = nn.Linear(hidden, dim)
                self.final_norm = final_norm
                self.ln_out = nn.LayerNorm(dim) if final_norm else nn.Identity()

        def forward(self, x: torch.Tensor) -> torch.Tensor:  # type: ignore
                x = self.fc1(x)
                x = self.act(x)
                x = self.ln_hidden(x)
                x = self.do(x)
                x = self.fc2(x)
                x = self.ln_out(x)
                return x


def build_embedding_head(version: str = 'v1', **kwargs) -> nn.Module:
    """Factory for embedding reconstruction heads.

    Args:
        version: 'v1' (basic) or 'v2' (enhanced). Aliases accepted.
        **kwargs: forwarded to underlying constructor. Supported for v2:
            - dim, hidden, dropout, final_norm
    """
    v = version.lower()
    if v in ('v2','enhanced','ln'):
        return EmbeddingReconstructionHeadV2(**kwargs)
    if v in ('v1','basic','simple'):
        # Strip kwargs that v1 does not understand to avoid TypeError
        filtered = {k: kwargs[k] for k in ('dim','hidden') if k in kwargs}
        return EmbeddingReconstructionHead(**filtered)
    raise ValueError(f"Unknown head version: {version}")
