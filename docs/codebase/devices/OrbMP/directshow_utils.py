from comtypes import *
from comtypes.automation import VARIANT
import ctypes

# GUID Helper
def DEFINE_GUID(name, l, w1, w2, b1, b2, b3, b4, b5, b6, b7, b8):
    return GUID('{{{:08x}-{:04x}-{:04x}-{:02x}{:02x}-{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}}}'.format(
        l, w1, w2, b1, b2, b3, b4, b5, b6, b7, b8))

# Standard GUIDs
CLSID_SystemDeviceEnum = DEFINE_GUID('CLSID_SystemDeviceEnum', 0x62BE5D10, 0x60EB, 0x11D0, 0xBD, 0x3B, 0x00, 0xA0, 0xC9, 0x11, 0xCE, 0x86)
CLSID_VideoInputDeviceCategory = DEFINE_GUID('CLSID_VideoInputDeviceCategory', 0x860BB310, 0x5D01, 0x11D0, 0xBD, 0x3B, 0x00, 0xA0, 0xC9, 0x11, 0xCE, 0x86)
IID_IKsTopologyInfo = DEFINE_GUID('IID_IKsTopologyInfo', 0x720D4AC0, 0x7533, 0x11D0, 0xA5, 0xD6, 0x28, 0xDB, 0x04, 0xC1, 0x00, 0x00)
IID_IKsControl = DEFINE_GUID('IID_IKsControl', 0x28F54685, 0x06FD, 0x11D2, 0xB2, 0x7A, 0x00, 0xA0, 0xC9, 0x22, 0x31, 0x96)
IID_IBaseFilter = DEFINE_GUID('IID_IBaseFilter', 0x56a86895, 0x0ad4, 0x11ce, 0xb0, 0x3a, 0x00, 0x80, 0xc7, 0x6c, 0x37, 0x70)

# Logitech Extension Unit GUID
# {63610682-5070-49AB-B8CC-B3855E8D2256}
LOGITECH_XU_GUID = DEFINE_GUID('LOGITECH_XU_GUID', 0x63610682, 0x5070, 0x49AB, 0xB8, 0xCC, 0xB3, 0x85, 0x5E, 0x8D, 0x22, 0x56)

# Structures
class KSP_NODE(Structure):
    _fields_ = [
        ("Set", GUID),
        ("Id", c_ulong),
        ("Flags", c_ulong),
        ("NodeId", c_ulong),
        ("Reserved", c_ulong),
    ]

# Interfaces
class IKsControl(IUnknown):
    _iid_ = IID_IKsControl
    _methods_ = [
        COMMETHOD([], HRESULT, 'KsProperty',
                  (['in'], POINTER(KSP_NODE), 'Property'),
                  (['in'], c_ulong, 'PropertyLength'),
                  (['in', 'out'], c_void_p, 'PropertyData'),
                  (['in'], c_ulong, 'DataLength'),
                  (['out'], POINTER(c_ulong), 'BytesReturned')),
        COMMETHOD([], HRESULT, 'KsMethod',
                  (['in'], c_void_p, 'Method'),
                  (['in'], c_ulong, 'MethodLength'),
                  (['in', 'out'], c_void_p, 'MethodData'),
                  (['in'], c_ulong, 'DataLength'),
                  (['out'], POINTER(c_ulong), 'BytesReturned')),
        COMMETHOD([], HRESULT, 'KsEvent',
                  (['in'], c_void_p, 'Event'),
                  (['in'], c_ulong, 'EventLength'),
                  (['in', 'out'], c_void_p, 'EventData'),
                  (['in'], c_ulong, 'DataLength'),
                  (['out'], POINTER(c_ulong), 'BytesReturned')),
    ]

class IKsTopologyInfo(IUnknown):
    _iid_ = IID_IKsTopologyInfo
    _methods_ = [
        COMMETHOD([], HRESULT, 'get_NumCategories',
                  (['out'], POINTER(c_ulong), 'pNumCategories')),
        COMMETHOD([], HRESULT, 'get_Category',
                  (['in'], c_ulong, 'dwIndex'),
                  (['out'], POINTER(GUID), 'pCategory')),
        COMMETHOD([], HRESULT, 'get_NumConnections',
                  (['out'], POINTER(c_ulong), 'pNumConnections')),
        # Skipping get_Connection definition for now as we don't need it
        COMMETHOD([], HRESULT, 'get_NumNodes',
                  (['out'], POINTER(c_ulong), 'pNumNodes')),
        COMMETHOD([], HRESULT, 'get_NodeName',
                  (['in'], c_ulong, 'dwNodeId'),
                  (['out'], c_void_p, 'pwchNodeName'), # String buffer
                  (['in'], c_ulong, 'dwBufSize'),
                  (['out'], POINTER(c_ulong), 'pdwNameLen')),
        COMMETHOD([], HRESULT, 'get_NodeType',
                  (['in'], c_ulong, 'dwNodeId'),
                  (['out'], POINTER(GUID), 'pNodeType')),
        COMMETHOD([], HRESULT, 'CreateNodeInstance',
                  (['in'], c_ulong, 'dwNodeId'),
                  (['in'], POINTER(GUID), 'iid'),
                  (['out'], POINTER(c_void_p), 'ppvObject')),
    ]

# DirectShow enumeration helpers needed often
# ICreateDevEnum, IEnumMoniker, IMoniker, IPropertyBag
# These can often be grabbed from comtypes.gen.DirectShowLib if available, or defined manually.
# For simplicity, we assume we can get the filter via other means or define minimally.

class IMoniker(IUnknown):
    _iid_ = GUID('{0000000f-0000-0000-C000-000000000046}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'BindToObject',
                  (['in'], c_void_p, 'pbc'),
                  (['in'], c_void_p, 'pmkToLeft'),
                  (['in'], POINTER(GUID), 'riidResult'),
                  (['out'], POINTER(c_void_p), 'ppvResult')),
        # ... others omitted ...
    ]

class IPropertyBag(IUnknown):
    _iid_ = GUID('{55272A00-42CB-11CE-8135-00AA004BB851}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'Read',
                  (['in'], c_void_p, 'pszPropName'), # LPCOLESTR
                  (['in', 'out'], POINTER(VARIANT), 'pVar'),
                  (['in'], c_void_p, 'pErrorLog')),
        # ...
    ]

class IEnumMoniker(IUnknown):
    _iid_ = GUID('{00000102-0000-0000-C000-000000000046}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'Next',
                  (['in'], c_ulong, 'celt'),
                  (['out'], POINTER(POINTER(IMoniker)), 'rgelt'),
                  (['out'], POINTER(c_ulong), 'pceltFetched')),
        # ...
    ]

class ICreateDevEnum(IUnknown):
    _iid_ = GUID('{29840822-5B84-11D0-BD3B-00A0C911CE86}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'CreateClassEnumerator',
                  (['in'], POINTER(GUID), 'clsidDeviceClass'),
                  (['out'], POINTER(POINTER(IEnumMoniker)), 'ppEnumMoniker'),
                  (['in'], c_ulong, 'dwFlags')),
    ]
