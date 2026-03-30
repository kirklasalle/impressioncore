from pathlib import Path

# We import the scanner as a module to access internal functions
from src.dev_tools.archive import archive_scanner as scanner


def write_temp_file(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "sample_module.py"
    p.write_text(content, encoding="utf-8")
    return p


def test_detect_markers_positive(tmp_path: Path, monkeypatch):
    content = '"""\nTitle: Sample\nStatus: Archived\n"""\n# body\n'
    f = write_temp_file(tmp_path, content)
    monkeypatch.setattr(scanner, "SRC_ROOT", tmp_path)  # redirect root
    assert scanner.detect_markers(f) is True


def test_detect_markers_negative(tmp_path: Path, monkeypatch):
    content = '"""Module with no marker"""\n'
    f = write_temp_file(tmp_path, content)
    monkeypatch.setattr(scanner, "SRC_ROOT", tmp_path)
    assert scanner.detect_markers(f) is False


def test_find_candidates(tmp_path: Path, monkeypatch):
    positive = '"""Status: Archived"""\n'
    negative = '"""clean file"""\n'
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "a.py").write_text(positive, encoding="utf-8")
    (tmp_path / "pkg" / "b.py").write_text(negative, encoding="utf-8")
    monkeypatch.setattr(scanner, "SRC_ROOT", tmp_path)
    cands = scanner.find_candidates()
    assert len(cands) == 1
    assert cands[0].name == "a.py"


def test_archive_path_computation(tmp_path: Path, monkeypatch):
    content = '"""Status: Archived"""\n'
    pkg = tmp_path / "nested" / "mod"
    pkg.mkdir(parents=True)
    file_path = pkg / "module.py"
    file_path.write_text(content, encoding="utf-8")
    monkeypatch.setattr(scanner, "SRC_ROOT", tmp_path)
    monkeypatch.setattr(scanner, "ARCHIVE_ROOT", tmp_path / "archive")
    archive_dest = scanner.compute_archive_path(file_path)
    assert archive_dest.as_posix().endswith("archive/nested/mod/module.py")


def test_write_shim(tmp_path: Path, monkeypatch):
    # ensure shim creation writes expected warning
    module = '"""Status: Archived"""\n'
    f = write_temp_file(tmp_path, module)
    monkeypatch.setattr(scanner, "SRC_ROOT", tmp_path)
    # override archive root to local tmp archive
    monkeypatch.setattr(scanner, "ARCHIVE_ROOT", tmp_path / "archive")
    # simulate move
    rel = f.relative_to(tmp_path)
    dest = scanner.ARCHIVE_ROOT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("# archived copy", encoding="utf-8")
    scanner.write_shim(f, rel)
    shim_text = f.read_text(encoding="utf-8")
    assert "DeprecationWarning" in shim_text
    assert "archived" in shim_text.lower()
