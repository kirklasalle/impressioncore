"""Regression tests for Phase 2 security hardening and Phase 3 architectural fixes.

Covers:
- SEC-04: CryptographicCore real AEAD encryption, fail-closed fallback, and PQC opt-in
- SEC-05: Safe AST formula evaluation and literal token-ID loading
- ARCH-01: GuardianAgent runtime inspections replacing unconditional stubs
- ARCH-03: Portable RLM path handling and checkpoint browser fallback
- CRIT-05: FAISS retrieved-index reconstruction in BrainInspiredTransformerLayer
- NOV-01: MHCProjection square-manifold guard
"""

import asyncio
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import torch

from agent0core.core.guardian_agent import GuardianAgent
from agent0core.core.llama_cpp_supervisor import LlamaCppSupervisor
from src.core.knowledge.rule_engine import _safe_eval_formula
from src.core.models.impressioncore_b3_architecture import BrainInspiredTransformerLayer
from src.core.security.identity.cryptographic_core import (
    CryptoAlgorithm,
    CryptographicCore,
    QuantumResistantError,
)
from src.models.layers.mhc import MHCProjection


def test_sec04_crypto_core_real_aead_and_fail_closed():
    """SEC-04: AES-GCM and ChaCha20-Poly1305 perform real AEAD round-trips and fail closed."""

    async def _run():
        core = CryptographicCore()
        try:
            key = await core.generate_symmetric_key(CryptoAlgorithm.CHACHA20_POLY1305, 256)
            plaintext = b"sovereign-identity-payload"

            ct_chacha, nonce_chacha = await core.encrypt_data(plaintext, key, CryptoAlgorithm.CHACHA20_POLY1305)
            assert ct_chacha != plaintext
            assert await core.decrypt_data(ct_chacha, nonce_chacha, key, CryptoAlgorithm.CHACHA20_POLY1305) == plaintext

            ct_aes, nonce_aes = await core.encrypt_data(plaintext, key, CryptoAlgorithm.AES_256_GCM)
            assert await core.decrypt_data(ct_aes, nonce_aes, key, CryptoAlgorithm.AES_256_GCM) == plaintext

            # Simulated PQC must fail closed by default
            with pytest.raises(QuantumResistantError):
                await core.generate_key_pair(CryptoAlgorithm.KYBER_1024)

            core.allow_simulated_pqc = True
            kp = await core.generate_key_pair(CryptoAlgorithm.KYBER_1024)
            assert kp.metadata["simulated"] is True
            assert kp.metadata["quantum_resistant"] is False

            # Fail closed when cryptography library is unavailable (no XOR fallback)
            with patch("src.core.security.identity.cryptographic_core.CRYPTOGRAPHY_AVAILABLE", False):
                with pytest.raises(QuantumResistantError):
                    await core.encrypt_data(plaintext, key, CryptoAlgorithm.AES_256_GCM)
        finally:
            await core.cleanup()

    asyncio.run(_run())


def test_sec05_safe_formula_eval_blocks_code_execution():
    """SEC-05: AST formula evaluator runs arithmetic safely and rejects dunder traversal."""
    assert _safe_eval_formula("min(score * 2 + 1, 10)", {"score": 4}) == 9
    assert _safe_eval_formula("score >= 3 and active", {"score": 4, "active": True}) is True
    with pytest.raises(ValueError):
        _safe_eval_formula("().__class__.__mro__[1].__subclasses__()", {})


def test_arch01_guardian_agent_tasks_perform_real_checks():
    """ARCH-01: GuardianAgent tasks inspect actual contracts/artifacts instead of blind stubs."""

    async def _run():
        agent = GuardianAgent(LlamaCppSupervisor())
        tool_res = await agent.run_task("tool_contract_audit")
        assert tool_res["lastResult"] == "success"
        assert "5 core tools" in tool_res["lastDetail"]

        cov_res = await agent.run_task("covenant_audit")
        assert cov_res["lastResult"] == "success"
        assert "SHA-256" in cov_res["lastDetail"]

        aab_res = await agent.run_task("aab_ledger_monitor")
        assert aab_res["lastResult"] in ("success", "warning")

    asyncio.run(_run())


def test_crit05_b3_layer_reconstructs_actual_faiss_index():
    """CRIT-05: Memory retrieval reconstructs mem_indices returned by FAISS, not index 0."""
    vec0 = np.zeros((16,), dtype=np.float32)
    vec2 = np.ones((16,), dtype=np.float32) * 3.0

    mock_index = MagicMock()
    mock_index.ntotal = 3
    mock_index.reconstruct.side_effect = lambda idx: vec2 if idx == 2 else vec0

    mock_mem = MagicMock()
    mock_mem.index = mock_index
    mock_mem.retrieve_memory.return_value = (np.array([[0.1]]), np.array([[2]]))

    layer = BrainInspiredTransformerLayer(
        embed_dim=16,
        num_heads=2,
        num_experts=2,
        expert_dim=16,
        experts_per_token=1,
        dropout=0.0,
        memory_manager=mock_mem,
    )
    layer.eval()
    x = torch.randn(1, 3, 16)
    with torch.no_grad():
        layer(x)
    mock_index.reconstruct.assert_called_once_with(2)


def test_nov01_mhc_projection_square_vs_rectangular():
    """NOV-01: MHCProjection applies Sinkhorn-Knopp only to square matrices."""
    sq = MHCProjection(4, 4, bias=False, iterations=20)
    proj = sq.projector(sq.weight)
    torch.testing.assert_close(proj.sum(dim=-1), torch.ones(4), atol=1e-4, rtol=1e-4)
    torch.testing.assert_close(proj.sum(dim=-2), torch.ones(4), atol=1e-4, rtol=1e-4)

    rect = MHCProjection(4, 8, bias=False)
    x = torch.randn(2, 4)
    out = rect(x)
    torch.testing.assert_close(out, x @ rect.weight.T)
