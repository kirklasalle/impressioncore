"""Unit tests for the AESEncryption engine (src/core/security/encryption/aes_encryption.py)."""

import os
import tempfile
import pytest
try:
    from src.core.security.encryption.aes_encryption import AESEncryption, EncryptionConfig, EncryptionResult, DecryptionResult
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


@pytest.mark.skipif(not HAS_CRYPTOGRAPHY, reason="cryptography library not installed")
class TestAESEncryption:
    """Suite of tests for the AES encryption engine."""

    def test_key_generation(self):
        """Keys can be generated with a password and salt."""
        engine = AESEncryption()
        password = "super-secret-password"
        
        # Test key generation
        key, salt = engine.generate_key(password)
        assert len(key) == 32  # 256 bits
        assert len(salt) == 32  # salt size default

        # Regenerate with same salt should produce same key
        key2, salt2 = engine.generate_key(password, salt=salt)
        assert key == key2
        assert salt == salt2
        engine.cleanup()

    def test_encrypt_decrypt_roundtrip(self):
        """Encrypting and decrypting data returns the original plaintext."""
        engine = AESEncryption()
        password = "my-encryption-key"
        key, salt = engine.generate_key(password)

        plaintext = b"Hello, this is a very sensitive piece of data!"
        
        # Encrypt
        result = engine.encrypt(plaintext, key)
        assert isinstance(result, EncryptionResult)
        assert result.ciphertext != plaintext
        assert len(result.iv) == 16
        assert len(result.tag) == 16

        # Decrypt
        dec_result = engine.decrypt(result.ciphertext, key, result.iv, result.tag)
        assert isinstance(dec_result, DecryptionResult)
        assert dec_result.verified is True
        assert dec_result.plaintext == plaintext
        engine.cleanup()

    def test_decrypt_invalid_key_fails(self):
        """Decryption with an invalid key raises or returns verification failure."""
        engine = AESEncryption()
        password = "correct-password"
        key, salt = engine.generate_key(password)
        wrong_key, _ = engine.generate_key("wrong-password", salt=salt)

        plaintext = b"Highly confidential message"
        result = engine.encrypt(plaintext, key)

        # Decrypt with wrong key
        dec_result = engine.decrypt(result.ciphertext, wrong_key, result.iv, result.tag)
        assert dec_result.verified is False
        assert dec_result.plaintext == b""
        engine.cleanup()

    def test_file_encrypt_decrypt_roundtrip(self):
        """File encryption and decryption yields identical file contents."""
        engine = AESEncryption()
        password = "file-secret-pass"

        # Create a temp directory for files
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "input.txt")
            encrypted_file = os.path.join(tmpdir, "input.enc")
            decrypted_file = os.path.join(tmpdir, "decrypted.txt")

            original_data = b"This is some file content that must be secure. " * 100
            with open(input_file, "wb") as f:
                f.write(original_data)

            # Encrypt file
            meta_enc = engine.encrypt_file(input_file, encrypted_file, password)
            assert meta_enc["bytes_processed"] == len(original_data)
            assert os.path.exists(encrypted_file)

            # Decrypt file
            meta_dec = engine.decrypt_file(encrypted_file, decrypted_file, password)
            assert meta_dec["verified"] is True
            assert os.path.exists(decrypted_file)

            # Compare contents
            with open(decrypted_file, "rb") as f:
                decrypted_data = f.read()
            assert decrypted_data == original_data
        engine.cleanup()

    def test_get_metrics(self):
        """Engine exposes performance metrics."""
        engine = AESEncryption()
        password = "metrics-pass"
        key, salt = engine.generate_key(password)
        
        # Perform some ops to populate metrics
        engine.encrypt(b"data", key)
        metrics = engine.get_metrics()
        
        assert "operations" in metrics
        assert "performance" in metrics
        assert "timing" in metrics
        assert metrics["operations"]["keys_generated"] >= 1
        assert metrics["operations"]["encryptions"] >= 1
        engine.cleanup()
