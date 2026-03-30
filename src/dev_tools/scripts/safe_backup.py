import os
import sys
import zipfile
from datetime import datetime

RESERVED = {
    'CON','PRN','AUX','NUL',
    'COM1','COM2','COM3','COM4','COM5','COM6','COM7','COM8','COM9',
    'LPT1','LPT2','LPT3','LPT4','LPT5','LPT6','LPT7','LPT8','LPT9'
}

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def is_reserved_basename(path: str) -> bool:
    base = os.path.basename(path)
    name, _ext = os.path.splitext(base)
    return name.upper() in RESERVED


def iter_files():
    # Include docs/ and .github/*.md plus select top-level files
    include_roots = [
        os.path.join(ROOT, 'docs'),
        os.path.join(ROOT, '.github'),
    ]
    top_level_includes = [
        os.path.join(ROOT, 'requirements.txt'),
        os.path.join(ROOT, 'manage_f_models.py'),
    ]

    # Top-level *.md
    for name in os.listdir(ROOT):
        if name.lower().endswith('.md') and not is_reserved_basename(name):
            yield os.path.join(ROOT, name)

    # Specific top-level files
    for p in top_level_includes:
        if os.path.isfile(p) and not is_reserved_basename(p):
            yield p

    # Walk include roots
    for base in include_roots:
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            # Skip reserved device names at any level
            dirnames[:] = [d for d in dirnames if not is_reserved_basename(d)]
            for f in filenames:
                full = os.path.join(dirpath, f)
                if is_reserved_basename(full):
                    continue
                # Only include markdown under .github to keep size small
                if os.path.commonpath([base, os.path.join(ROOT, '.github')]) == os.path.join(ROOT, '.github'):
                    if not f.lower().endswith('.md'):
                        continue
                yield full


def main():
    backups = os.path.join(ROOT, 'backups')
    os.makedirs(backups, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = os.path.join(backups, f'checkpoint_{ts}.zip')
    count = 0
    with zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for f in iter_files():
            arcname = os.path.relpath(f, ROOT)
            zf.write(f, arcname)
            count += 1
    print(f'Backup created: {dest} ({count} files)')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Backup failed: {e}', file=sys.stderr)
        sys.exit(1)
