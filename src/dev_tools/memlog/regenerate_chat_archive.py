"""Utility: regenerate a chat history archive from memlog entries.

Scans `src/memlog/` for recent memlog entries and writes a single archive file.
"""
from __future__ import annotations

import os
from datetime import datetime


def find_memlog_files(root: str = "src/memlog") -> list:
    files = []
    for name in os.listdir(root):
        p = os.path.join(root, name)
        if os.path.isfile(p) and name.endswith(".md"):
            files.append(p)
    return sorted(files)


def build_archive(out_path: str = "src/memlog/chat_history_archive_$(date).md"):
    files = find_memlog_files()
    now = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = out_path.replace("$(date)", now)
    with open(out, "w", encoding="utf-8") as fo:
        fo.write(f"# Chat history archive Generated: {now}\n\n")
        for f in files:
            fo.write(f"## {os.path.basename(f)}\n\n")
            try:
                with open(f, encoding="utf-8") as fi:
                    fo.write(fi.read())
                    fo.write("\n\n---\n\n")
            except Exception:
                fo.write("(failed to read)\n\n")
    print("Wrote archive:", out)


if __name__ == "__main__":
    build_archive()
