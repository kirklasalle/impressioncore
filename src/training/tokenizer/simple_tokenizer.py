"""A tiny, reversible tokenizer for smoke/testing.

This is intentionally minimal: it maps printable ASCII to small ints and back.
"""


class SimpleTokenizer:
    def __init__(self, vocab_size: int = 16384):
        # map printable ASCII (32..126) into token ids; rest gets split by bytes
        self.vocab_size = vocab_size
        self.offset = 32

    def encode(self, text: str, max_len: int):
        ids = []
        for c in text:
            if len(ids) >= max_len:
                break
            code = ord(c)
            if 32 <= code <= 126:
                ids.append(code - self.offset + 1)  # reserve 0 for padding
            else:
                # split bytes for non-printable (fallback)
                for b in c.encode('utf-8', errors='ignore'):
                    if len(ids) >= max_len:
                        break
                    ids.append((b % (self.vocab_size - 1)) + 1)
        if len(ids) < max_len:
            ids.extend([0] * (max_len - len(ids)))
        return ids

    def decode(self, ids: list[int]):
        chars = []
        for i in ids:
            if i == 0:
                chars.append('\n')
            else:
                chars.append(chr((i - 1) + self.offset))
        return ''.join(chars)
