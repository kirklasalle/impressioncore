import sys
import torch
print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print(f"Torch Version: {torch.__version__}")
print(f"Torch CUDA Version: {torch.version.cuda}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device Name: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA not available. Possible reasons: Wrong Torch build (CPU only), Drivers missing, or Hardware not found.")
