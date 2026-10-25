"""Build script to generate the complete world-class HTML site for .mcp at D:\Projects\Websites\.mcp."""
import os
import pathlib
import sys

DEST = pathlib.Path(r"D:\Projects\Websites\.mcp")
DEST.mkdir(parents=True, exist_ok=True)
(DEST / "assets" / "images").mkdir(parents=True, exist_ok=True)

print(f"[BUILD] Target directory verified: {DEST}")
