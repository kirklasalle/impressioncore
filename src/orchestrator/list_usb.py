import usb.core
import usb.util


def list_usb():
    print("--- Detailed USB Device List ---")
    devices = usb.core.find(find_all=True)
    for dev in devices:
        try:
            manufacturer = usb.util.get_string(dev, dev.iManufacturer)
            product = usb.util.get_string(dev, dev.iProduct)
            print(f"VID: {dev.idVendor:04x} | PID: {dev.idProduct:04x} | {manufacturer} - {product}")
        except Exception:
            print(f"VID: {dev.idVendor:04x} | PID: {dev.idProduct:04x} | (No Desc)")

if __name__ == "__main__":
    list_usb()
