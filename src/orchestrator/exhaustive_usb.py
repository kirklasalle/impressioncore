import contextlib

import usb.core
import usb.util


def list_all_usb():
    print("--- Exhaustive USB Scan ---")
    # Find all devices on all buses
    devices = usb.core.find(find_all=True)
    count = 0
    for dev in devices:
        count += 1
        print(f"[{count}] VID: {dev.idVendor:04x} | PID: {dev.idProduct:04x}")
        # Try to get more info if possible
        with contextlib.suppress(Exception):
            print(f"    Class: {dev.bDeviceClass} | SubClass: {dev.bDeviceSubClass}")
    print(f"Total USB devices found: {count}")

if __name__ == "__main__":
    list_all_usb()
