import winreg

def scan_registry():
    path = r"SYSTEM\CurrentControlSet\Enum\USB"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
            i = 0
            while True:
                try:
                    sub_key_name = winreg.EnumKey(key, i)
                    if "VID_046D" in sub_key_name.upper():
                        print(f"Found Logitech Vendor: {sub_key_name}")
                        # Look for PID_08C2
                        with winreg.OpenKey(key, sub_key_name) as sub_key:
                            j = 0
                            while True:
                                try:
                                    inst_name = winreg.EnumKey(sub_key, j)
                                    print(f"  Instance: {inst_name}")
                                    # Try to read FriendlyName
                                    inst_path = f"{path}\\{sub_key_name}\\{inst_name}"
                                    try:
                                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, inst_path) as k:
                                            try:
                                                fname = winreg.QueryValueEx(k, "FriendlyName")[0]
                                                print(f"    FriendlyName: {fname}")
                                            except: pass
                                            try:
                                                desc = winreg.QueryValueEx(k, "DeviceDesc")[0]
                                                print(f"    DeviceDesc: {desc}")
                                            except: pass
                                            try:
                                                service = winreg.QueryValueEx(k, "Service")[0]
                                                print(f"    Service: {service}")
                                            except: pass
                                    except: pass
                                    j += 1
                                except WindowsError:
                                    break
                    i += 1
                except WindowsError:
                    break
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scan_registry()
