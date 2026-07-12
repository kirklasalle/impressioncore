# Critical Cleanup and Entry Points Consolidation

## Goal
Implement the three critical audit action items: remove and purge the 4GB database from git history, permanently delete the 386 empty python files, and consolidate the entry points to use `src/main.py` instead of root `main.py`.

## Tasks
- [x] Task 1: Commit existing unstaged modifications and deletions to ensure a clean working tree → Verify: `git status` reports no unstaged changes.
- [x] Task 2: Purge `src/core/vector_database_1.db` from Git history using `git filter-branch` or `git filter-repo` and add it to `.gitignore` → Verify: `.git` folder size is reduced and database is not tracked.
- [x] Task 3: Locate and permanently delete all empty (0-byte) `.py` files across the repository → Verify: Search for 0-byte `.py` files returns zero matches.
- [x] Task 4: Remove root `main.py` shim and update `launch_impressioncore.bat` to reference `src/main.py` directly → Verify: Launcher functions properly and no root-level shim exists.
- [ ] Task 5: Verify the system executes correctly post-cleanup → Verify: Run status check script or run test runner.

## Done When
- [ ] 4GB `vector_database_1.db` is purged from git history and added to `.gitignore`.
- [ ] All empty `.py` files are permanently deleted.
- [ ] Root `main.py` is removed, and launch scripts point to `src/main.py`.
