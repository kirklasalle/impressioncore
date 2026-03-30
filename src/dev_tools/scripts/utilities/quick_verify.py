#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts/utilities/quick_verify.py
**Category:** Source Code
**Status:** Active
"""


from pathlib import Path

f_path = Path('F:/data/datasets')
print('F: DRIVE VERIFICATION:')

for d in sorted(f_path.iterdir()):
    if d.is_dir():
        files = list(d.rglob('*'))
        if len(files) > 0:
            print(f'   SUCCESS {d.name} - {len(files)} files')
        else:
            print(f'   EMPTY {d.name}')
