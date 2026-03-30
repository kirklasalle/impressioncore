import hid
import sys

def scan_hid():
    print("Scanning HID devices...")
    try:
        devices = hid.enumerate()
        found = False
        for d in devices:
            vid = d['vendor_id']
            pid = d['product_id']
            # Logitech VID is 0x046d
            if vid == 0x046d:
                print(f"[!] Found Logitech HID Device: {hex(vid)}:{hex(pid)}")
                print(f"    Product: {d['product_string']}")
                print(f"    Path: {d['path']}")
                if pid == 0x08c2: # Orb MP
                    print("    *** TARGET DEVICE FOUND (HID Interface) ***")
                found = True
            else:
                # Uncomment to see all
                # print(f"Found Device: {hex(vid)}:{hex(pid)} {d['product_string']}")
                pass
                
        if not found:
            print("No Logitech HID devices found.")
            
    except Exception as e:
        print(f"Error enumerating HID: {e}")

if __name__ == "__main__":
    scan_hid()
