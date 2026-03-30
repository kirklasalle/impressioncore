
⚠️ ARCHIVED FILE
This file has been archived for historical, compatibility, or deprecation reasons. Do not modify or use in active development.

#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** System Generated  
**Tags:** #docs\archive\move_memlog.py #python #source_code  
**Category:** Archive  
**Status:** Archived
"""









# Move Memlog

**Created:** 2024-10-15  
**Updated:** 2025-07-26 10:27:00  
**Author:** System Generated  
**Tags:** #docs\archive\move_memlog.py #python #source_code  
**Category:** Archive  
**Status:** Archived

import shutil
import os

# Define source and destination paths
source_path = "d:\\Projects\\impressioncore\\memlog"
destination_path = "d:\\Projects\\impressioncore\\src\\memlog"

# Move the directory
if os.path.exists(source_path):
    shutil.move(source_path, destination_path)
    print(f"Moved {source_path} to {destination_path}")
else:
    print(f"Source path {source_path} does not exist.")