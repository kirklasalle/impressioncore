import ctypes
from ctypes import wintypes
import uuid

# GUIDs
CLSID_SystemDeviceEnum = uuid.UUID("{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}")
CLSID_VideoInputDeviceCategory = uuid.UUID("{860BB310-5D01-11D0-BD3B-00A0C911CE86}")
AM_KSCATEGORY_CAPTURE = uuid.UUID("{65E8773D-8F56-11D0-A3B9-00A0C9223196}")

class GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD), ("Data4", ctypes.c_byte * 8)]

def to_guid(u):
    b = u.bytes_le
    return GUID(
        wintypes.DWORD.from_buffer_copy(b[0:4]),
        wintypes.WORD.from_buffer_copy(b[4:6]),
        wintypes.WORD.from_buffer_copy(b[6:8]),
        (ctypes.c_byte * 8).from_buffer_copy(b[8:16])
    )

def list_ctypes(cat_guid_obj):
    print(f"\nScanning Category: {cat_guid_obj}")
    ole32 = ctypes.windll.ole32
    ole32.CoInitialize(None)
    
    # CreateDevEnum
    devenum = ctypes.c_void_p()
    clsid_devenum = to_guid(CLSID_SystemDeviceEnum)
    iid_devenum = to_guid(uuid.UUID("{29840822-5B84-11D0-BD3B-00A0C911CE86}"))
    hr = ole32.CoCreateInstance(ctypes.byref(clsid_devenum), None, 1, ctypes.byref(iid_devenum), ctypes.byref(devenum))
    if hr != 0:
        print(f"CoCreateInstance(DevEnum) failed: {hr:x}")
        return

    # CreateClassEnumerator
    enum_moniker = ctypes.c_void_p()
    cat_guid = to_guid(cat_guid_obj)
    # vtable: index 3 is CreateClassEnumerator
    VTBL_TYPE = ctypes.WINFUNCTYPE(wintypes.HRESULT, ctypes.c_void_p, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p), wintypes.DWORD)
    vtbl = ctypes.cast(devenum, ctypes.POINTER(ctypes.c_void_p))
    create_enum = VTBL_TYPE(ctypes.cast(vtbl[0], ctypes.POINTER(ctypes.c_void_p))[3])
    
    hr = create_enum(devenum, ctypes.byref(cat_guid), ctypes.byref(enum_moniker), 0)
    if hr != 0 or not enum_moniker:
        print(f"CreateClassEnumerator failed: {hr:x}")
        return

    # IEnumMoniker::Next
    NEXT_TYPE = ctypes.WINFUNCTYPE(wintypes.HRESULT, ctypes.c_void_p, wintypes.ULONG, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(wintypes.ULONG))
    vtbl_enum = ctypes.cast(enum_moniker, ctypes.POINTER(ctypes.c_void_p))
    enum_next = NEXT_TYPE(ctypes.cast(vtbl_enum[0], ctypes.POINTER(ctypes.c_void_p))[3])
    
    while True:
        moniker = ctypes.c_void_p()
        fetched = wintypes.ULONG(0)
        hr = enum_next(enum_moniker, 1, ctypes.byref(moniker), ctypes.byref(fetched))
        if hr != 0 or fetched.value == 0:
            break
            
        print(f"  [+] Found Moniker at {moniker.value:x}")
        
        # GetDisplayName (index 20)
        DISPLAY_TYPE = ctypes.WINFUNCTYPE(wintypes.HRESULT, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(wintypes.LPWSTR))
        vtbl_mon = ctypes.cast(moniker, ctypes.POINTER(ctypes.c_void_p))
        get_display = DISPLAY_TYPE(ctypes.cast(vtbl_mon[0], ctypes.POINTER(ctypes.c_void_p))[20])
        
        display_name = wintypes.LPWSTR()
        hr = get_display(moniker, None, None, ctypes.byref(display_name))
        if hr == 0:
            print(f"      Display Name: {display_name.value}")
            ole32.CoTaskMemFree(display_name)
        else:
            print(f"      GetDisplayName failed: {hr:x}")
            
        # BindToStorage (index 9) -> IPropertyBag
        BIND_TYPE = ctypes.WINFUNCTYPE(wintypes.HRESULT, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p))
        bag_iid = to_guid(uuid.UUID("{55272a00-42cb-11ce-8135-00aa004bb851}"))
        bind_to_storage = BIND_TYPE(ctypes.cast(vtbl_mon[0], ctypes.POINTER(ctypes.c_void_p))[9])
        
        bag = ctypes.c_void_p()
        hr = bind_to_storage(moniker, None, None, ctypes.byref(bag_iid), ctypes.byref(bag))
        if hr == 0:
            print(f"      Successfully bound to IPropertyBag at {bag.value:x}")
            # IPropertyBag::Read (index 3)
            READ_TYPE = ctypes.WINFUNCTYPE(wintypes.HRESULT, ctypes.c_void_p, wintypes.LPWSTR, ctypes.c_void_p, ctypes.c_void_p)
            vtbl_bag = ctypes.cast(bag, ctypes.POINTER(ctypes.c_void_p))
            read_prop = READ_TYPE(ctypes.cast(vtbl_bag[0], ctypes.POINTER(ctypes.c_void_p))[3])
            
            def print_prop(pname):
                var = ctypes.create_string_buffer(24) # VARIANT is 16-24 bytes
                # Clear variant
                ctypes.memset(var, 0, 24)
                hr = read_prop(bag, pname, var, None)
                if hr == 0:
                    vt = wintypes.WORD.from_buffer_copy(var[0:2])
                    if vt == 8: # VT_BSTR
                        bstr_val = ctypes.cast(wintypes.WPARAM.from_buffer_copy(var[8:16]), wintypes.LPWSTR)
                        print(f"        {pname}: {bstr_val.value}")
                else:
                    # print(f"        {pname} Read failed: {hr:x}")
                    pass

            print_prop("FriendlyName")
            print_prop("Description")
            print_prop("DevicePath")
        else:
            print(f"      BindToStorage failed: {hr:x}")

if __name__ == "__main__":
    list_ctypes(CLSID_VideoInputDeviceCategory)
    list_ctypes(AM_KSCATEGORY_CAPTURE)
