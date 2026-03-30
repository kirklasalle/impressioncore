"""Tests for src.core.security.user.User class."""

import pathlib
import uuid

import pytest

# Load user.py directly to avoid the broken import chain in
# src.core.security.__init__ (missing identity_manager module).
# The source file also contains a corrupted literal "\n" on line 174 that
# breaks normal import, so we read only up to (but not including) the
# ``if __name__`` guard and exec that fragment.
_user_path = pathlib.Path(__file__).resolve().parents[2] / "core" / "security" / "user.py"
_src_lines = _user_path.read_text(encoding="utf-8").splitlines(keepends=True)
# Find the end of the class (just before `if __name__`)
_cut = next(i for i, l in enumerate(_src_lines) if l.strip().startswith("if __name__"))
_ns: dict = {}
exec(compile("".join(_src_lines[:_cut]), str(_user_path), "exec"), _ns)
User = _ns["User"]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_personal_data():
    """Minimal personal_data dict reused across tests."""
    return {"name": "Ada Lovelace", "date_of_birth": "1815-12-10"}


@pytest.fixture
def user(sample_personal_data):
    """Standard User instance for tests that just need a valid user."""
    return User(
        username="ada",
        password="Analytic4lEngine!",
        email="ada@example.com",
        personal_data=sample_personal_data,
    )


# ---------------------------------------------------------------------------
# __init__ tests
# ---------------------------------------------------------------------------

class TestInit:
    """Tests for User.__init__."""

    def test_user_id_is_valid_uuid(self, user):
        """user_id must be a valid UUID-4 string."""
        parsed = uuid.UUID(user.user_id, version=4)
        assert str(parsed) == user.user_id

    def test_two_users_get_different_ids(self, sample_personal_data):
        u1 = User("a", "pw", "a@b.com", sample_personal_data)
        u2 = User("a", "pw", "a@b.com", sample_personal_data)
        assert u1.user_id != u2.user_id

    def test_username_stored(self, user):
        assert user.username == "ada"

    def test_email_stored(self, user):
        assert user.email == "ada@example.com"

    def test_personal_data_stored(self, user, sample_personal_data):
        assert user.personal_data == sample_personal_data

    def test_password_not_stored_in_plaintext(self, user):
        assert "Analytic4lEngine!" not in user.password_hash

    def test_password_hash_format(self, user):
        """Hash format is '<hex-salt>:<hex-sha256>'."""
        parts = user.password_hash.split(":")
        assert len(parts) == 2
        salt_hex, hash_hex = parts
        # salt is 16 bytes → 32 hex chars
        assert len(salt_hex) == 32
        # SHA-256 → 64 hex chars
        assert len(hash_hex) == 64

    def test_security_questions_initially_empty(self, user):
        assert user.security_questions == {}

    def test_authentication_factors_initially_empty(self, user):
        assert user.authentication_factors == []

    def test_empty_username(self, sample_personal_data):
        u = User("", "pw", "e@e.com", sample_personal_data)
        assert u.username == ""

    def test_empty_email(self, sample_personal_data):
        u = User("u", "pw", "", sample_personal_data)
        assert u.email == ""

    def test_empty_personal_data(self):
        u = User("u", "pw", "e@e.com", {})
        assert u.personal_data == {}


# ---------------------------------------------------------------------------
# _hash_password tests
# ---------------------------------------------------------------------------

class TestHashPassword:
    """Tests for User._hash_password."""

    def test_returns_string(self, user):
        assert isinstance(user._hash_password("test"), str)

    def test_different_hashes_for_same_password(self, user):
        """Random salt means the same plaintext produces different stored hashes."""
        h1 = user._hash_password("samepassword")
        h2 = user._hash_password("samepassword")
        assert h1 != h2

    def test_hash_contains_colon_separator(self, user):
        h = user._hash_password("anything")
        assert ":" in h

    def test_hash_empty_password(self, user):
        h = user._hash_password("")
        parts = h.split(":")
        assert len(parts) == 2 and len(parts[1]) == 64

    def test_hash_unicode_password(self, user):
        h = user._hash_password("пароль密码🔑")
        parts = h.split(":")
        assert len(parts) == 2 and len(parts[1]) == 64

    def test_hash_very_long_password(self, user):
        long_pw = "A" * 100_000
        h = user._hash_password(long_pw)
        parts = h.split(":")
        assert len(parts) == 2 and len(parts[1]) == 64


# ---------------------------------------------------------------------------
# verify_password tests
# ---------------------------------------------------------------------------

class TestVerifyPassword:
    """Tests for User.verify_password."""

    def test_correct_password_returns_true(self, sample_personal_data):
        u = User("u", "secret", "e@e.com", sample_personal_data)
        assert u.verify_password("secret") is True

    def test_wrong_password_returns_false(self, user):
        assert user.verify_password("wrong") is False

    def test_empty_password_when_set_empty(self):
        u = User("u", "", "e@e.com", {})
        assert u.verify_password("") is True

    def test_empty_password_when_set_nonempty(self, user):
        assert user.verify_password("") is False

    def test_case_sensitivity(self, sample_personal_data):
        u = User("u", "Secret", "e@e.com", sample_personal_data)
        assert u.verify_password("secret") is False
        assert u.verify_password("SECRET") is False
        assert u.verify_password("Secret") is True

    def test_unicode_password_verify(self):
        pw = "пароль密码🔑"
        u = User("u", pw, "e@e.com", {})
        assert u.verify_password(pw) is True
        assert u.verify_password("wrong") is False

    def test_very_long_password_verify(self):
        long_pw = "B" * 100_000
        u = User("u", long_pw, "e@e.com", {})
        assert u.verify_password(long_pw) is True
        assert u.verify_password(long_pw + "x") is False

    def test_whitespace_only_password(self):
        u = User("u", "   ", "e@e.com", {})
        assert u.verify_password("   ") is True
        assert u.verify_password("") is False


# ---------------------------------------------------------------------------
# add_security_question / verify_security_question tests
# ---------------------------------------------------------------------------

class TestSecurityQuestions:
    """Tests for add_security_question and verify_security_question."""

    def test_add_security_question_stores_entry(self, user):
        user.add_security_question("Pet?", "dog")
        assert "Pet?" in user.security_questions

    def test_answer_is_hashed_not_plaintext(self, user):
        user.add_security_question("Color?", "blue")
        assert user.security_questions["Color?"] != "blue"

    def test_answer_hash_has_correct_format(self, user):
        user.add_security_question("Q?", "A")
        stored = user.security_questions["Q?"]
        parts = stored.split(":")
        assert len(parts) == 2
        assert len(parts[0]) == 32
        assert len(parts[1]) == 64

    def test_verify_nonexistent_question_returns_false(self, user):
        assert user.verify_security_question("NoSuchQ?", "any") is False

    def test_verify_security_question_known_behavior(self, user):
        """
        NOTE: verify_security_question re-hashes the answer with a NEW random
        salt, so it will virtually never match the stored hash. This test
        documents that current behavior (likely a bug).
        """
        user.add_security_question("Pet?", "dog")
        # Due to random salt, verification is expected to fail
        assert user.verify_security_question("Pet?", "dog") is False

    def test_overwrite_security_question(self, user):
        user.add_security_question("Q?", "first")
        user.add_security_question("Q?", "second")
        # Only one entry for the same question key
        assert len(user.security_questions) == 1

    def test_multiple_questions(self, user):
        user.add_security_question("Q1?", "A1")
        user.add_security_question("Q2?", "A2")
        assert len(user.security_questions) == 2

    def test_unicode_question_and_answer(self, user):
        user.add_security_question("好きな色？", "青い")
        assert "好きな色？" in user.security_questions


# ---------------------------------------------------------------------------
# add_authentication_factor tests
# ---------------------------------------------------------------------------

class TestAuthenticationFactor:
    """Tests for add_authentication_factor."""

    def test_add_single_factor(self, user):
        user.add_authentication_factor("totp")
        assert user.authentication_factors == ["totp"]

    def test_add_multiple_factors(self, user):
        user.add_authentication_factor("totp")
        user.add_authentication_factor("fingerprint")
        assert user.authentication_factors == ["totp", "fingerprint"]

    def test_duplicate_factors_allowed(self, user):
        user.add_authentication_factor("totp")
        user.add_authentication_factor("totp")
        assert len(user.authentication_factors) == 2

    def test_empty_string_factor(self, user):
        user.add_authentication_factor("")
        assert user.authentication_factors == [""]

    def test_factors_preserve_order(self, user):
        for f in ["a", "b", "c"]:
            user.add_authentication_factor(f)
        assert user.authentication_factors == ["a", "b", "c"]
