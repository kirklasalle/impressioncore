#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts/utilities/cache_migration_script.py #transformer
**Category:** Source Code
**Status:** Active
"""



import json
import os
import shutil
import time
from datetime import datetime
from pathlib import Path


class HuggingFaceCacheMigrator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Common HuggingFace cache locations on Windows
        self.possible_cache_paths = [
            Path.home() / ".cache" / "huggingface",
            Path(os.environ.get('APPDATA', '')) / "huggingface",
            Path(os.environ.get('LOCALAPPDATA', '')) / "huggingface",
            Path("C:/Users") / os.environ.get('USERNAME', '') / ".cache" / "huggingface"
        ]

        self.target_cache_path = Path("F:/downloads/huggingface_cache")

        self.migration_log = {
            "start_time": datetime.now().isoformat(),
            "source_paths_found": [],
            "migrated_files": [],
            "total_size_mb": 0,
            "errors": []
        }

    def find_existing_cache(self):
        """Find existing HuggingFace cache directories."""
        found_caches = []

        print("🔍 Searching for existing HuggingFace cache directories...")

        for cache_path in self.possible_cache_paths:
            if cache_path.exists() and cache_path.is_dir():
                # Calculate size
                try:
                    total_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
                    size_mb = total_size / (1024 * 1024)

                    if size_mb > 10:  # Only consider caches > 10MB
                        found_caches.append({
                            "path": cache_path,
                            "size_mb": size_mb,
                            "file_count": len(list(cache_path.rglob('*')))
                        })

                        print(f"✅ Found cache: {cache_path}")
                        print(f"   Size: {size_mb:.1f} MB")
                        print(f"   Files: {len(list(cache_path.rglob('*')))}")

                except Exception as e:
                    print(f"⚠️ Error checking {cache_path}: {e}")

        self.migration_log["source_paths_found"] = [str(c["path"]) for c in found_caches]
        return found_caches

    def migrate_cache(self, source_cache):
        """Migrate cache from source to F:/downloads/huggingface_cache."""
        source_path = source_cache["path"]

        print(f"\n📦 Migrating cache from: {source_path}")
        print(f"   Target: {self.target_cache_path}")

        # Create target directory
        self.target_cache_path.mkdir(parents=True, exist_ok=True)

        try:
            start_time = time.time()

            # If target already has content, merge
            if any(self.target_cache_path.iterdir()):
                print("🔄 Merging with existing cache...")
                for item in source_path.iterdir():
                    target_item = self.target_cache_path / item.name

                    if item.is_file():
                        if not target_item.exists():
                            shutil.copy2(item, target_item)
                            self.migration_log["migrated_files"].append(str(item))
                    elif item.is_dir():
                        if target_item.exists():
                            # Merge directories
                            shutil.copytree(item, target_item, dirs_exist_ok=True)
                        else:
                            shutil.copytree(item, target_item)
                        self.migration_log["migrated_files"].append(str(item))
            else:
                # Full migration
                print("📋 Full cache migration...")
                shutil.copytree(source_path, self.target_cache_path, dirs_exist_ok=True)
                self.migration_log["migrated_files"] = [str(f) for f in source_path.rglob('*')]

            elapsed_time = time.time() - start_time

            # Calculate migrated size
            migrated_size = sum(f.stat().st_size for f in self.target_cache_path.rglob('*') if f.is_file()) / (1024 * 1024)
            self.migration_log["total_size_mb"] = migrated_size

            print("✅ Migration completed!")
            print(f"   Time: {elapsed_time:.1f} seconds")
            print(f"   Size: {migrated_size:.1f} MB")

            return True

        except Exception as e:
            error_msg = f"Migration failed: {e}"
            print(f"❌ {error_msg}")
            self.migration_log["errors"].append(error_msg)
            return False

    def cleanup_old_cache(self, source_caches):
        """Clean up old cache directories after successful migration."""
        print("\n🧹 Cleaning up old cache directories...")

        for cache_info in source_caches:
            source_path = cache_info["path"]

            try:
                print(f"   Removing: {source_path}")
                shutil.rmtree(source_path)
                print(f"   ✅ Removed: {source_path}")

            except Exception as e:
                print(f"   ⚠️ Could not remove {source_path}: {e}")
                self.migration_log["errors"].append(f"Cleanup failed for {source_path}: {e}")

    def update_environment_variables(self):
        """Update environment variables to point to new cache location."""
        print("\n⚙️ Updating environment variables...")

        cache_path = str(self.target_cache_path)

        os.environ['HF_HOME'] = cache_path
        os.environ['TRANSFORMERS_CACHE'] = cache_path
        os.environ['HF_DATASETS_CACHE'] = cache_path

        print("✅ Environment variables updated:")
        print(f"   HF_HOME = {cache_path}")
        print(f"   TRANSFORMERS_CACHE = {cache_path}")
        print(f"   HF_DATASETS_CACHE = {cache_path}")

    def save_migration_log(self):
        """Save migration log for audit trail."""
        log_file = f"cache_migration_log_{self.timestamp}.json"

        self.migration_log["end_time"] = datetime.now().isoformat()

        with open(log_file, 'w') as f:
            json.dump(self.migration_log, f, indent=2)

        print(f"📊 Migration log saved: {log_file}")

    def run_migration(self):
        """Execute complete cache migration."""
        print("🚀 HuggingFace Cache Migration to F: Drive")
        print("=" * 50)

        # Find existing caches
        found_caches = self.find_existing_cache()

        if not found_caches:
            print("ℹ️ No significant HuggingFace cache found on C: drive")
            self.update_environment_variables()
            return True

        print(f"\n📋 Found {len(found_caches)} cache directories")
        total_size = sum(c["size_mb"] for c in found_caches)
        print(f"   Total size to migrate: {total_size:.1f} MB")

        # Check F: drive space
        try:
            total, used, free = shutil.disk_usage("F:/")
            free_gb = free / (1024**3)
            required_gb = total_size / 1024

            print(f"   F: drive free space: {free_gb:.1f} GB")
            print(f"   Required space: {required_gb:.1f} GB")

            if free_gb < required_gb + 10:  # 10GB buffer
                print("❌ Insufficient space on F: drive for migration")
                return False

        except Exception as e:
            print(f"⚠️ Could not check F: drive space: {e}")

        # Perform migration
        success = True
        for cache_info in found_caches:
            if not self.migrate_cache(cache_info):
                success = False
                break

        if success:
            self.update_environment_variables()

            # Ask user before cleanup
            print("\n⚠️ Migration successful! Clean up old cache directories?")
            print("This will free up space on C: drive.")
            print("Proceeding with cleanup in 10 seconds...")
            time.sleep(10)

            self.cleanup_old_cache(found_caches)

        self.save_migration_log()

        print("\n" + "=" * 50)
        print("🎉 Cache Migration Complete!")
        print(f"✅ Migrated: {self.migration_log['total_size_mb']:.1f} MB")
        print(f"❌ Errors: {len(self.migration_log['errors'])}")

        return success

def main():
    """Main execution function."""
    migrator = HuggingFaceCacheMigrator()

    print("⚠️ CACHE MIGRATION WARNING:")
    print("This will move HuggingFace cache from C: to F: drive")
    print("This is necessary to prevent C: drive from filling up")
    print("Migration will preserve all downloaded data")

    # Check current C: drive space
    try:
        total, used, free = shutil.disk_usage("C:/")
        free_gb = free / (1024**3)
        used_gb = used / (1024**3)
        print("\nC: Drive Status:")
        print(f"   Free: {free_gb:.1f} GB")
        print(f"   Used: {used_gb:.1f} GB")

        if free_gb < 5:
            print("🚨 CRITICAL: C: drive has less than 5GB free!")

    except Exception as e:
        print(f"Could not check C: drive space: {e}")

    print("\nProceeding with migration in 5 seconds...")
    time.sleep(5)

    success = migrator.run_migration()

    if success:
        print("\n🎯 Next Steps:")
        print("1. Cache successfully migrated to F:/downloads/huggingface_cache")
        print("2. Environment variables updated")
        print("3. Ready to continue dataset acquisition")
        print("4. Run: python enhanced_dataset_acquisition.py")
    else:
        print("\n❌ Migration failed. Check logs for details.")

    return success

if __name__ == "__main__":
    main()
