"""
add_archive_notice.py

This script adds a deprecation/archive notice to the top of every file in docs/archive/ and src/archive/.

Encoding & Error Handling Policy:
    - All file I/O uses UTF-8 encoding.
    - If a UnicodeDecodeError or UnicodeEncodeError occurs, the error is logged with file path and error type.
    - If errors='ignore' is used, a warning is logged that data loss is possible.
    - All exceptions during file I/O are logged with full context for traceability.

Author: GitHub Copilot
Date: August 9, 2025
"""
import os

NOTICE_MD = """# ⚠️ ARCHIVED FILE\nThis file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.\n\n"""
NOTICE_PY = """\n⚠️ ARCHIVED FILE\nThis file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.\n\n"""

ARCHIVE_DIRS = [
    os.path.join('docs', 'archive'),
    os.path.join('src', 'archive'),
]

EXT_MD = {'.md', '.yaml', '.yml', '.html'}
EXT_PY = {'.py', '.css'}

def add_notice(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in EXT_MD:
        notice = NOTICE_MD
    elif ext in EXT_PY:
        notice = NOTICE_PY
    else:
        return
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError as ude:
        print(f"[UNICODE ERROR] Could not decode file: {filepath} | {ude}")
        return
    except Exception as e:
        print(f"[ERROR] Could not read file: {filepath} | {type(e).__name__}: {e}")
        return
    if notice.strip() in content:
        return  # Already has notice
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(notice + content)
    except UnicodeEncodeError as uee:
        print(f"[UNICODE ERROR] Could not encode file: {filepath} | {uee}")
    except Exception as e:
        print(f"[ERROR] Could not write file: {filepath} | {type(e).__name__}: {e}")

def main():
    for archive_dir in ARCHIVE_DIRS:
        for root, _, files in os.walk(archive_dir):
            for fname in files:
                fpath = os.path.join(root, fname)
                add_notice(fpath)
    print("Archive notices added to all archived files.")

if __name__ == "__main__":
    main()
