import comtypes
import ctypes

def main():
    print("Listing Running COM Objects (ROT)...")
    try:
        ole32 = ctypes.windll.ole32
        rot = ctypes.POINTER(comtypes.IUnknown)()
        hr = ole32.GetRunningObjectTable(0, ctypes.byref(rot))
        if hr != 0:
            print(f"Failed to get ROT (HR: {hr:x})")
            return
            
        rot = rot.QueryInterface(comtypes.persist.IRunningObjectTable)
        
        enum_moniker = rot.EnumRunning()
        
        while True:
            moniker_ptr, fetched = enum_moniker.Next(1)
            if fetched == 0 or not moniker_ptr:
                break
            
            moniker = moniker_ptr.QueryInterface(comtypes.persist.IMoniker)
            
            pbc = ctypes.POINTER(comtypes.IUnknown)()
            ole32.CreateBindCtx(0, ctypes.byref(pbc))
            bc = pbc.QueryInterface(comtypes.persist.IBindCtx)
            
            name = moniker.GetDisplayName(bc, None)
            print(f"  [+] {name}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
