import winreg

def scan_registry(key, path, search_term):
    try:
        with winreg.OpenKey(key, path) as k:
            i = 0
            while True:
                try:
                    name = winreg.EnumKey(k, i)
                    try:
                        with winreg.OpenKey(k, name) as subkey:
                            try:
                                val, _ = winreg.QueryValueEx(subkey, "")
                                if search_term.lower() in str(val).lower():
                                    print(f"[{path}\\{name}] -> {val}")
                            except Exception:
                                pass
                    except Exception:
                        pass
                    i += 1
                except OSError:
                    break
    except Exception:
        pass

def main():
    print("Scanning Registry for Logitech/Orbit...")
    scan_registry(winreg.HKEY_CLASSES_ROOT, "CLSID", "Logitech")
    scan_registry(winreg.HKEY_CLASSES_ROOT, "CLSID", "Orbit")
    scan_registry(winreg.HKEY_CLASSES_ROOT, "CLSID", "Sphere")
    scan_registry(winreg.HKEY_CLASSES_ROOT, "", "Logitech")
    scan_registry(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Classes\\CLSID", "Logitech")

if __name__ == "__main__":
    main()
