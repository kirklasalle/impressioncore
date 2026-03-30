"""
Kinect & Multi-Camera Probe
===========================
Lists all available video devices with their friendly names
to identify the Kinect v1 (Xbox 360) and Orbit cameras.
"""
import logging
import ctypes
from ctypes import wintypes
import comtypes
import comtypes.client
import cv2

# DirectShow Context
CLSID_SystemDeviceEnum = "{62BE5D10-60EB-11D0-BD3B-00A0C911CE86}"
CLSID_VideoInputDeviceCategory = "{860BB310-5D01-11D0-BD3B-00A0C911CE86}"

# Interfaces
class IPropertyBag(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Read",
            (['in'], wintypes.LPWSTR, "pszPropName"),
            (['in', 'out'], ctypes.POINTER(comtypes.automation.VARIANT), "pVar"),
            (['in'], ctypes.c_void_p, "pErrorLog"))
    ]

class IEnumMoniker(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{00000102-0000-0000-C000-000000000046}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "Next",
            (['in'], wintypes.ULONG, "celt"),
            (['out'], ctypes.POINTER(ctypes.POINTER(comtypes.IUnknown)), "rgelt"),
            (['out'], ctypes.POINTER(wintypes.ULONG), "pceltFetched")),
        # Skiping others for brevity
    ]

class IMoniker(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{0000010f-0000-0000-C000-000000000046}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "BindToObject",
            (['in'], ctypes.c_void_p, "pbc"),
            (['in'], ctypes.c_void_p, "pmkToLeft"),
            (['in'], ctypes.POINTER(comtypes.GUID), "riidResult"),
            (['out'], ctypes.POINTER(ctypes.c_void_p), "ppvResult")),
        comtypes.COMMETHOD([], comtypes.HRESULT, "BindToStorage",
            (['in'], ctypes.c_void_p, "pbc"),
            (['in'], ctypes.c_void_p, "pmkToLeft"),
            (['in'], ctypes.POINTER(comtypes.GUID), "riid"),
            (['out'], ctypes.POINTER(ctypes.c_void_p), "ppvObj")),
        # Leaving others
    ]

class ICreateDevEnum(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{29840822-5B84-11D0-BD3B-00A0C911CE86}")
    _methods_ = [
        comtypes.COMMETHOD([], comtypes.HRESULT, "CreateClassEnumerator",
            (['in'], ctypes.POINTER(comtypes.GUID), "clsidDeviceClass"),
            (['out'], ctypes.POINTER(ctypes.POINTER(IEnumMoniker)), "ppEnumMoniker"),
            (['in'], wintypes.DWORD, "dwFlags"))
    ]

def list_devices():
    print("="*60)
    print("  DirectShow Camera Enumeration")
    print("="*60)
    
    try:
        devenum = comtypes.client.CreateObject(
            CLSID_SystemDeviceEnum,
            clsctx=comtypes.CLSCTX_INPROC_SERVER,
            interface=ICreateDevEnum
        )
        
        cat_guid = comtypes.GUID(CLSID_VideoInputDeviceCategory)
        enum_moniker = devenum.CreateClassEnumerator(ctypes.byref(cat_guid), 0)
        
        if not enum_moniker:
            print("No video devices category found.")
            return

        index = 0
        while True:
            moniker_ptr = ctypes.POINTER(comtypes.IUnknown)()
            fetched = wintypes.ULONG()
            res = enum_moniker.Next(1, ctypes.byref(moniker_ptr), ctypes.byref(fetched))
            
            if fetched.value == 0:
                break
                
            moniker = moniker_ptr.QueryInterface(IMoniker)
            
            # Get Property Bag
            IPropertyBag_IID = comtypes.GUID("{55272a00-42cb-11ce-8135-00aa004bb851}")
            bag_ptr = ctypes.c_void_p()
            moniker.BindToStorage(None, None, ctypes.byref(IPropertyBag_IID), ctypes.byref(bag_ptr))
            
            bag = ctypes.cast(bag_ptr, ctypes.POINTER(IPropertyBag)).contents
            
            var = comtypes.automation.VARIANT()
            bag.Read("FriendlyName", ctypes.byref(var), None)
            name = str(var.value)
            
            bag.Read("DevicePath", ctypes.byref(var), None)
            path = str(var.value)
            
            print(f"Device [{index}]: {name}")
            print(f"  Path: {path}")
            
            # Simple probe for resolution
            try:
                cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                if cap.isOpened():
                    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    print(f"  Current: {int(w)}x{int(h)}")
                    cap.release()
            except:
                print("  Failed to open via OpenCV")
            
            print("-" * 30)
            index += 1
            
    except Exception as e:
        print(f"Error enumerating devices: {e}")

if __name__ == "__main__":
    list_devices()
