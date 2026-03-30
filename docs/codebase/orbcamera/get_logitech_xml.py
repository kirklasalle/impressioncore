"""
Download and Extract Debian Package
=====================================
Downloads uvcdynctrl-data.deb and extracts logitech.xml
"""
import urllib.request
import os
import subprocess
import tarfile
import shutil

URL = "http://ftp.us.debian.org/debian/pool/main/libw/libwebcam/uvcdynctrl-data_0.2.5-2_all.deb"
DEB_FILE = "uvcdynctrl-data.deb"

def main():
    print(f"Downloading {URL}...")
    try:
        urllib.request.urlretrieve(URL, DEB_FILE)
        print("Download complete.")
    except Exception as e:
        print(f"Download failed: {e}")
        return

    print("Extracting DEB file...")
    # DEB files are 'ar' archives. Windows usually doesn't have 'ar'.
    # But 7z often can handle it, or we can look for raw offsets.
    # The data.tar.gz usually starts with 1F 8B
    
    with open(DEB_FILE, 'rb') as f:
        content = f.read()
        
    # Find gzip header (0x1F 0x8B) for data.tar.gz
    # There might be multiple (control.tar.gz and data.tar.gz)
    # data.tar.gz is typically the larger second one.
    
    parts = []
    offset = 0
    while True:
        try:
            # Look for gzip header
            idx = content.find(b'\x1f\x8b', offset)
            if idx == -1:
                break
            parts.append(idx)
            offset = idx + 2
        except:
            break
            
    print(f"Found potential gzip streams at: {parts}")
    
    # Try extracting each stream
    found_xml = False
    
    for i, start_idx in enumerate(parts):
        print(f"Processing stream {i} at {start_idx}...")
        try:
            with open(f"stream_{i}.tar.gz", 'wb') as f:
                f.write(content[start_idx:])
            
            try:
                with tarfile.open(f"stream_{i}.tar.gz", 'r:gz') as tar:
                    for member in tar.getmembers():
                        if "logitech.xml" in member.name:
                            print(f"  FOUND: {member.name}")
                            tar.extract(member, path=".")
                            # Move to current dir if nested
                            if os.path.exists(member.name):
                                base = os.path.basename(member.name)
                                shutil.copy(member.name, base)
                                print(f"  Extracted to: {base}")
                                found_xml = True
            except Exception as e:
                print(f"  Not a valid tar.gz or read error: {e}")
                
        except Exception as e:
            print(f"  Error processing stream: {e}")

    if found_xml:
        print("\nSUCCESS! logitech.xml extracted.")
        with open("logitech.xml", "r") as f:
            print("\n--- CONTENT PREVIEW ---")
            print(f.read()[:500])
    else:
        print("\nFailed to extract logitech.xml")

if __name__ == "__main__":
    main()
