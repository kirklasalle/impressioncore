import wmi

c = wmi.WMI()
print("Scanning PnP Entities for Audio Terms...")
found = 0
for dev in c.Win32_PnPEntity(ConfigManagerErrorCode=0):
    name = str(dev.Name)
    # Check broadly
    keywords = ["audio", "mic", "sound", "camera", "playstation", "eye", "usb"]
    if any(k in name.lower() for k in keywords):
        print(f"Name: '{name}'")
        found += 1

print(f"Total Matches: {found}")
