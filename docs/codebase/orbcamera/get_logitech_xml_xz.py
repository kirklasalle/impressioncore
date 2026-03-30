"""
Download and Extract Debian Package (XZ Support)
==================================================
Downloads uvcdynctrl-data.deb and extracts logitech.xml
Updated to detect XZ streams (modern Debian packages).
"""
import urllib.request
import os
import tarfile
import shutil
import lzma

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

    print("Scanning DEB file for compression streams...")
    
    with open(DEB_FILE, 'rb') as f:
        content = f.read()
        
    parts = []
    
    # 1. Look for GZIP (1F 8B)
    offset = 0
    while True:
        idx = content.find(b'\x1f\x8b', offset)
        if idx == -1: break
        # Simple heuristic: must be followed by 0x08 (deflate) usually
        if idx + 2 < len(content) and content[idx+2] == 0x08:
            print(f"  Found GZIP candidate at {idx}")
            parts.append(('gz', idx))
        offset = idx + 2
        
    # 2. Look for XZ (FD 37 7A 58 5A 00)
    offset = 0
    while True:
        idx = content.find(b'\xfd\x37\x7a\x58\x5a\x00', offset)
        if idx == -1: break
        print(f"  Found XZ candidate at {idx}")
        parts.append(('xz', idx))
        offset = idx + 6

    if not parts:
        print("No compressed streams found!")
        return

    found_xml = False
    
    for type_str, start_idx in parts:
        print(f"Processing {type_str} stream at {start_idx}...")
        try:
            # Write stream to temp file
            ext = "tar.gz" if type_str == 'gz' else "tar.xz"
            with open(f"temp.{ext}", 'wb') as f:
                f.write(content[start_idx:])
            
            try:
                mode = 'r:gz' if type_str == 'gz' else 'r:xz'
                with tarfile.open(f"temp.{ext}", mode) as tar:
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
                print(f"  Extract error: {e}")
                
        except Exception as e:
            print(f"  Stream write error: {e}")

    if found_xml:
        print("\nSUCCESS! logitech.xml extracted.")
        with open("logitech.xml", "r") as f:
            print("\n--- CONTENT PREVIEW ---")
            print(f.read()[:500])
    else:
        print("\nFailed to extract logitech.xml")

if __name__ == "__main__":
    main()
