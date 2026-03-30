import comtypes
import comtypes.client
import ctypes
from ctypes import wintypes

CLSID_SystemDeviceEnum = "{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}"
CLSID_VideoInputDeviceCategory = "{860BB310-5D01-11D0-BD3B-00A0C911CE86}"
IID_ICreateDevEnum = "{29840822-5B84-11D0-BD3B-00A0C911CE86}"

class ICreateDevEnum(comtypes.IUnknown):
    _iid_ = comtypes.GUID(IID_ICreateDevEnum)
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "CreateClassEnumerator",
                    (['in'], comtypes.GUID, "clsidDeviceClass"),
                    (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "ppEnumMoniker"),
                    (['in'], wintypes.ULONG, "dwFlags")),
    ]

def main():
    print("DirectShow Device Check...")
    categories = {
        "Video Input": "{860BB310-5D01-11D0-BD3B-00A0C911CE86}",
        "Video Capture": "{E5323777-F976-4f5b-9C55-B94699C46E44}", # AM_KSCATEGORY_CAPTURE
        "Video": "{69917243-bd97-11d0-ab1e-00a0c9223196}", # AM_KSCATEGORY_VIDEO
        "Audio Input": "{33D9A762-90C8-11d0-BD43-00A0C911CE86}",
    }
    
    try:
        devenum = comtypes.client.CreateObject(CLSID_SystemDeviceEnum, 
                                              clsctx=comtypes.CLSCTX_INPROC_SERVER,
                                              interface=ICreateDevEnum)
        print("Created SystemDeviceEnum")
        
        for name, guid_str in categories.items():
            cat_guid = comtypes.GUID(guid_str)
            enum_moniker_ptr = devenum.CreateClassEnumerator(cat_guid, 0)
            
            if not enum_moniker_ptr:
                print(f"[-] No monikers found for {name} ({guid_str}).")
            else:
                print(f"[+] Found monikers for {name} ({guid_str}).")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
