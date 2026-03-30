import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path.cwd()))

# Import and run the simple test
try:
    from src.models.lora.test_simple_lora import main
    print("Successfully imported the test module")
    main()
except Exception as e:
    print(f"Error occurred: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
