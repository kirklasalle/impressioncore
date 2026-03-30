

try:
    import pygrabber.dshow_core as core
    print("Core dir:", dir(core))
    if hasattr(core, 'IPropertyBag'):
        print("FOUND IPropertyBag in dshow_core")
    else:
        print("IPropertyBag NOT in dshow_core")
except ImportError as e:
    print(f"ImportError dshow_core: {e}")

try:
    import comtypes.gen
    print("Comtypes gen:", dir(comtypes.gen))
except Exception:
    pass
