import usb.core
import usb.util
import usb.backend.libusb1
import os
import sys

VID = 0x046d
PID = 0x08c2

def get_backend():
    is_64bits = sys.maxsize > 2**32
    arch_str = 'VS2015-x64' if is_64bits else 'VS2015-Win32'
    base_dir = os.path.dirname(__file__)
    candidate_paths = [
        os.path.join(base_dir, 'libusb_dist', 'libusb-1.0.26-binaries', arch_str, 'dll', 'libusb-1.0.dll'),
        os.path.join(base_dir, 'libusb_dist', arch_str, 'dll', 'libusb-1.0.dll'),
    ]
    for dll_path in candidate_paths:
        if os.path.exists(dll_path):
            return usb.backend.libusb1.get_backend(find_library=lambda x: dll_path)
    return None

def debug_control():
    print("Initializing USB Debug...")
    backend = get_backend()
    dev = usb.core.find(idVendor=VID, idProduct=PID, backend=backend)
    
    if not dev:
        print("Device not found.")
        return

    print("Device Found.")
    
    # 1. Try Set Configuration
    print("Setting Configuration...")
    try:
        dev.set_configuration()
        print("  Set Config OK")
    except Exception as e:
        print(f"  Set Config Failed: {e}")

    # 2. Try Claim Interface 0 (VC)
    print("Claiming Interface 0...")
    try:
        # usb.util.claim_interface(dev, 0) # pyusb claims automatically usually
        # But we can try explicit
        if dev.is_kernel_driver_active(0):
            print("  Kernel Driver Active: Detaching...")
            dev.detach_kernel_driver(0)
        
        usb.util.claim_interface(dev, 0)
        print("  Claim Interface 0 OK")
    except Exception as e:
        print(f"  Claim Interface 0 Failed: {e}")
        # On Windows 'NotImplementedError' for detach is native.
        # But fail to claim often means 'Access Denied'.

    # 3. Try Standard GET_DESCRIPTOR (Device)
    print("Testing Standard Control Transfer (GET_DESCRIPTOR)...")
    try:
        # ReqType 0x80 (Dev->Host, Std, Dev), Req 0x06 (GetDesc), Val 0x0100 (Dev), Idx 0
        desc = dev.ctrl_transfer(0x80, 0x06, 0x0100, 0, 18)
        print(f"  GET_DESCRIPTOR OK. Length: {len(desc)}")
    except Exception as e:
        print(f"  GET_DESCRIPTOR Failed: {e}")

if __name__ == "__main__":
    debug_control()
