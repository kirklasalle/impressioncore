#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #memory_management #python #source_code #src/brainsim/memory/backup_and_version_uks.py
**Category:** Source Code
**Status:** Active
"""









# Backup And Version Uks

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:00
# Author:** ImpressionCore Team
# Tags:** #memory_management #python #source_code #src\\brainsim\\memory\\backup_and_version_uks.py
# Category:** Source Code
# Status:** Active

"""
Backup and versioning script for UKS and aggregated data (ImpressionCore-b1 Phase 3).
- Copies and timestamps UKS and aggregated data files to a backup directory on F:/
- Keeps a changelog of all backups
"""
import os
import shutil
from datetime import datetime

UKS_PATH = "F:/impressioncore-b1-uks-output/uks_db.pkl"
AGG_PATH = "F:/impressioncore-b1-uks-output/aggregated_data.pkl"
BACKUP_DIR = "F:/impressioncore-b1-uks-output/backups/"
CHANGELOG = os.path.join(BACKUP_DIR, "backup_changelog.txt")

os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_file(src, backup_dir, label):
    if not os.path.exists(src):
        print(f"[WARN] {src} does not exist, skipping.")
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(backup_dir, f"{label}_{ts}.pkl")
    shutil.copy2(src, dst)
    print(f"[INFO] Backed up {src} to {dst}")
    return dst

def log_backup(changelog, files):
    with open(changelog, "a") as f:
        f.write(f"Backup at {datetime.now().isoformat()}\n")
        for label, path in files.items():
            f.write(f"  {label}: {path}\n")
        f.write("\n")

def main():
    files = {}
    files['uks_db'] = backup_file(UKS_PATH, BACKUP_DIR, "uks_db")
    files['aggregated_data'] = backup_file(AGG_PATH, BACKUP_DIR, "aggregated_data")
    log_backup(CHANGELOG, files)
    print("[SUCCESS] Backup and versioning complete.")

if __name__ == "__main__":
    main()
