import os
import shutil
from pathlib import Path

def safe_move(src, dst):
    src_path = Path(src)
    dst_path = Path(dst)
    
    if not src_path.exists():
        print(f"Source {src_path} does not exist. Skipping.")
        return
        
    if dst_path.exists():
        print(f"Destination {dst_path} already exists. Merging contents...")
        for item in src_path.iterdir():
            dest_item = dst_path / item.name
            if dest_item.exists():
                print(f"  Conflict: {dest_item} already exists. Skipping {item.name}.")
            else:
                print(f"  Moving {item} to {dest_item}")
                shutil.move(str(item), str(dest_item))
        print(f"Removing empty source directory {src_path}")
        try:
            src_path.rmdir()
        except OSError:
            print(f"  Could not remove {src_path} (might not be empty).")
    else:
        print(f"Moving {src_path} to {dst_path}")
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))

def main():
    print("--- Reorganizing F: Drive ---")
    
    # 1. Move F:\models\embeddings to F:\data\embeddings\models_embeddings
    safe_move(r"F:\models\embeddings", r"F:\data\embeddings\models_embeddings")
    
    # 2. Move F:\data\training\checkpoints to F:\models\checkpoints\data_training_checkpoints
    safe_move(r"F:\data\training\checkpoints", r"F:\models\checkpoints\data_training_checkpoints")
    
    # 3. Move F:\data\english-grammar to F:\data\datasets\english-grammar
    safe_move(r"F:\data\english-grammar", r"F:\data\datasets\english-grammar")
    
    print("--- Reorganization Complete ---")

if __name__ == "__main__":
    main()
