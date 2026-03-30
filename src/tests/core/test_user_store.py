"""Tests for UserStore class in src.core.security.user_store."""

import importlib.util
import json
import os
import sys
import types

import pytest

# ---------------------------------------------------------------------------
# Direct module loading — bypass src.core.security.__init__.py which imports
# subpackages (identity, monitoring, …) that may not be fully installed.
# ---------------------------------------------------------------------------

def _ensure_package(name: str, path: str):
    """Register a namespace package stub if not already in sys.modules."""
    if name not in sys.modules:
        pkg = types.ModuleType(name)
        pkg.__path__ = [path]
        pkg.__package__ = name
        sys.modules[name] = pkg


def _load_module(name: str, filepath: str, package: str):
    """Load a single .py file as *name* inside *package*, skipping __init__."""
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = package
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Ensure namespace stubs so relative imports inside user_store.py resolve.
_ensure_package("src", os.path.join("src"))
_ensure_package("src.core", os.path.join("src", "core"))
_ensure_package("src.core.security", os.path.join("src", "core", "security"))

_user_mod = _load_module(
    "src.core.security.user",
    os.path.join("src", "core", "security", "user.py"),
    "src.core.security",
)
_store_mod = _load_module(
    "src.core.security.user_store",
    os.path.join("src", "core", "security", "user_store.py"),
    "src.core.security",
)

User = _user_mod.User
UserStore = _store_mod.UserStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def store(tmp_path):
    """Return a UserStore backed by a temporary directory."""
    return UserStore(storage_path=str(tmp_path / "users"))


@pytest.fixture()
def sample_user():
    """Return a freshly-created User object."""
    return User(
        username="alice",
        password="s3cret!",
        email="alice@example.com",
        personal_data={"name": "Alice"},
    )


# ---------------------------------------------------------------------------
# __init__ tests
# ---------------------------------------------------------------------------


class TestInit:
    def test_creates_storage_directory(self, tmp_path):
        target = str(tmp_path / "new_store")
        assert not os.path.exists(target)
        UserStore(storage_path=target)
        assert os.path.isdir(target)

    def test_existing_directory_is_accepted(self, tmp_path):
        target = str(tmp_path / "existing")
        os.makedirs(target)
        store = UserStore(storage_path=target)
        assert store.storage_path == target

    def test_default_storage_path(self, monkeypatch, tmp_path):
        """Default path is 'user_data' relative to cwd."""
        monkeypatch.chdir(tmp_path)
        store = UserStore()
        assert store.storage_path == "user_data"
        assert os.path.isdir(str(tmp_path / "user_data"))


# ---------------------------------------------------------------------------
# store_user / get_user tests
# ---------------------------------------------------------------------------


class TestStoreAndGetUser:
    def test_store_creates_json_file(self, store, sample_user):
        store.store_user(sample_user)
        expected = os.path.join(store.storage_path, "alice.json")
        assert os.path.isfile(expected)

    def test_stored_file_contains_valid_json(self, store, sample_user):
        store.store_user(sample_user)
        path = os.path.join(store.storage_path, "alice.json")
        with open(path) as f:
            data = json.load(f)
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"

    def test_get_user_returns_user_object(self, store, sample_user):
        store.store_user(sample_user)
        retrieved = store.get_user("alice")
        assert isinstance(retrieved, User)
        assert retrieved.username == "alice"
        assert retrieved.email == "alice@example.com"

    def test_get_user_preserves_personal_data(self, store, sample_user):
        store.store_user(sample_user)
        retrieved = store.get_user("alice")
        assert retrieved.personal_data == {"name": "Alice"}

    def test_get_nonexistent_user_returns_none(self, store):
        assert store.get_user("nonexistent") is None

    def test_store_duplicate_overwrites(self, store, sample_user):
        store.store_user(sample_user)
        sample_user.email = "newalice@example.com"
        store.store_user(sample_user)
        retrieved = store.get_user("alice")
        assert retrieved.email == "newalice@example.com"


# ---------------------------------------------------------------------------
# list_users tests
# ---------------------------------------------------------------------------


class TestListUsers:
    def test_empty_store(self, store):
        assert store.list_users() == []

    def test_single_user(self, store, sample_user):
        store.store_user(sample_user)
        assert store.list_users() == ["alice"]

    def test_multiple_users(self, store):
        for name in ("alice", "bob", "charlie"):
            store.create_user(username=name, password="pw", email=f"{name}@x.com")
        assert sorted(store.list_users()) == ["alice", "bob", "charlie"]

    def test_ignores_non_json_files(self, store, sample_user):
        store.store_user(sample_user)
        with open(os.path.join(store.storage_path, "readme.txt"), "w") as f:
            f.write("ignore me")
        assert store.list_users() == ["alice"]


# ---------------------------------------------------------------------------
# create_user tests
# ---------------------------------------------------------------------------


class TestCreateUser:
    def test_returns_user_object(self, store):
        user = store.create_user("bob", "pw123", "bob@example.com")
        assert isinstance(user, User)
        assert user.username == "bob"

    def test_persists_to_disk(self, store):
        store.create_user("bob", "pw123", "bob@example.com")
        assert "bob" in store.list_users()

    def test_with_personal_data(self, store):
        pd = {"age": 30, "city": "NYC"}
        user = store.create_user("bob", "pw123", "bob@example.com", personal_data=pd)
        assert user.personal_data == pd

    def test_default_personal_data_none(self, store):
        user = store.create_user("bob", "pw123", "bob@example.com")
        assert user.personal_data is None

    def test_roundtrip_preserves_email(self, store):
        store.create_user("bob", "pw123", "bob@example.com")
        retrieved = store.get_user("bob")
        assert retrieved.email == "bob@example.com"


# ---------------------------------------------------------------------------
# edit_user tests
# ---------------------------------------------------------------------------


class TestEditUser:
    def test_edit_email(self, store):
        store.create_user("bob", "pw", "old@example.com")
        updated = store.edit_user("bob", email="new@example.com")
        assert updated.email == "new@example.com"
        assert store.get_user("bob").email == "new@example.com"

    def test_edit_password(self, store):
        store.create_user("bob", "original", "bob@example.com")
        updated = store.edit_user("bob", password="changed")
        assert updated.username == "bob"

    def test_edit_personal_data(self, store):
        store.create_user("bob", "pw", "bob@example.com", personal_data={"k": "v"})
        updated = store.edit_user("bob", personal_data={"k": "v2", "extra": True})
        assert updated.personal_data == {"k": "v2", "extra": True}

    def test_edit_nonexistent_raises(self, store):
        with pytest.raises(ValueError, match="User not found"):
            store.edit_user("ghost", email="x@x.com")

    def test_edit_no_changes(self, store):
        store.create_user("bob", "pw", "bob@example.com")
        updated = store.edit_user("bob")
        assert updated.username == "bob"
        assert updated.email == "bob@example.com"


# ---------------------------------------------------------------------------
# delete_user tests
# ---------------------------------------------------------------------------


class TestDeleteUser:
    def test_delete_removes_file(self, store):
        store.create_user("bob", "pw", "bob@example.com")
        store.delete_user("bob")
        assert not os.path.exists(os.path.join(store.storage_path, "bob.json"))

    def test_delete_removes_from_listing(self, store):
        store.create_user("bob", "pw", "bob@example.com")
        store.delete_user("bob")
        assert "bob" not in store.list_users()

    def test_delete_nonexistent_raises(self, store):
        with pytest.raises(ValueError, match="User not found"):
            store.delete_user("ghost")

    def test_get_after_delete_returns_none(self, store):
        store.create_user("bob", "pw", "bob@example.com")
        store.delete_user("bob")
        assert store.get_user("bob") is None


# ---------------------------------------------------------------------------
# Full CRUD cycle
# ---------------------------------------------------------------------------


class TestCrudCycle:
    def test_create_read_update_delete(self, store):
        # Create
        user = store.create_user("kirk", "pass1", "kirk@ic.ai", {"role": "admin"})
        assert user.username == "kirk"

        # Read
        fetched = store.get_user("kirk")
        assert fetched.email == "kirk@ic.ai"
        assert fetched.personal_data == {"role": "admin"}

        # Update
        store.edit_user("kirk", email="kirk2@ic.ai")
        fetched = store.get_user("kirk")
        assert fetched.email == "kirk2@ic.ai"

        # Delete
        store.delete_user("kirk")
        assert store.get_user("kirk") is None
        assert "kirk" not in store.list_users()


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_empty_username(self, store):
        """An empty username should still work at the filesystem level."""
        user = store.create_user("", "pw", "empty@example.com")
        assert user.username == ""
        assert os.path.isfile(os.path.join(store.storage_path, ".json"))

    def test_special_characters_in_username(self, store):
        """Usernames with special (but filesystem-safe) characters."""
        store.create_user("user-name_123", "pw", "u@example.com")
        assert store.get_user("user-name_123").email == "u@example.com"

    def test_unicode_username(self, store):
        store.create_user("héllo", "pw", "h@example.com")
        fetched = store.get_user("héllo")
        assert fetched is not None
        assert fetched.email == "h@example.com"

    def test_large_personal_data(self, store):
        big = {f"key_{i}": f"value_{i}" for i in range(500)}
        store.create_user("big", "pw", "big@example.com", personal_data=big)
        fetched = store.get_user("big")
        assert fetched.personal_data == big

    def test_multiple_stores_same_directory(self, tmp_path):
        """Two UserStore instances sharing a directory see the same data."""
        path = str(tmp_path / "shared")
        s1 = UserStore(storage_path=path)
        s2 = UserStore(storage_path=path)
        s1.create_user("shared_user", "pw", "s@x.com")
        assert "shared_user" in s2.list_users()
