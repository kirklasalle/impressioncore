"""Tokenization shim.

Provides minimal placeholder interfaces so legacy tests importing
`tokenization` or nested modules don't fail. Real implementation can
replace these stubs during Phase 2+ consolidation.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_VOCAB = {"<pad>": 0, "<unk>": 1}


@dataclass
class SimpleTokenizer:
    vocab: dict
    unk_token: str = "<unk>"

    def encode(self, text: str) -> list[int]:
        return [self.vocab.get(tok, self.vocab[self.unk_token]) for tok in text.split()]

    def decode(self, ids: list[int]) -> str:
        inv = {v: k for k, v in self.vocab.items()}
        return " ".join(inv.get(i, self.unk_token) for i in ids)


_INSTANCE: SimpleTokenizer | None = None


def get_tokenizer() -> SimpleTokenizer:
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = SimpleTokenizer(vocab=DEFAULT_VOCAB)
    return _INSTANCE

__all__ = ["SimpleTokenizer", "get_tokenizer"]
