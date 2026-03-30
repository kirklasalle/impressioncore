
import sys
import os
import traceback

print(f"CWD: {os.getcwd()}")
sys.path.append(os.getcwd())

print("Attempting import...")
try:
    from src.core.models.impressioncore_b3_architecture import ImpressionCoreB3Model
    print("SUCCESS: Imported ImpressionCoreB3Model")
except Exception as e:
    print(f"FAILURE: {e}")
    traceback.print_exc()
