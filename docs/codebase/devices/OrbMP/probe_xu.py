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

def probe_xu():
    backend = get_backend()
    dev = usb.core.find(idVendor=VID, idProduct=PID, backend=backend)
    if not dev:
        print("Device not found.")
        return

    # Assuming Interface 0 is VC
    INTERFACE = 0
    
    # Candidate Units to probe
    UNITS = [3, 4, 8, 9, 10]
    
    # UVC Constants
    UVC_GET_LEN = 0x85
    UVC_GET_CUR = 0x81
    UVC_GET_INFO = 0x86
    
    REQ_TYPE_GET = 0xA1 # Dir: Dev->Host (1), Type: Class (01), Recip: Interface (00001)

    print(f"Probing UVC XU on Interface {INTERFACE}...")
    
    for unit_id in UNITS:
        print(f"\n--- Probing Unit ID: {unit_id} ---")
        
        # Probe controls 1 to 16
        for cs in range(1, 17):
            wValue = (cs << 8)
            wIndex = (unit_id << 8) | INTERFACE
            
            try:
                # GET_LEN
                length = dev.ctrl_transfer(REQ_TYPE_GET, UVC_GET_LEN, wValue, wIndex, 2)
                if len(length) == 2:
                    val_len = length[0] + (length[1] << 8)
                    print(f"  CS {cs}: Found! Length = {val_len} bytes")
                    
                    # Try GET_CUR
                    try:
                        cur = dev.ctrl_transfer(REQ_TYPE_GET, UVC_GET_CUR, wValue, wIndex, val_len)
                        print(f"       Current Value: {list(cur)}")
                    except Exception as e:
                        print(f"       GET_CUR Failed: {e}")
                else:
                    print(f"  CS {cs}: Unexpected Len Response: {list(length)}")
            except usb.core.USBError as e:
                # Pipe error usually means control not supported
                if e.errno == 13 or "Pipe" in str(e): # Access denied or Pipe error
                    # print(f"  CS {cs}: Not supported")
                    pass
                else:
                    print(f"  CS {cs}: Error {e}")

if __name__ == "__main__":
    probe_xu()
