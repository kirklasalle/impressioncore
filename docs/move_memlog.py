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