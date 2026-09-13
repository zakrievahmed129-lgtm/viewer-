import ctypes
from ctypes import wintypes

class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmPositionX", ctypes.c_long),
        ("dmPositionY", ctypes.c_long),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", wintypes.WCHAR * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]

class DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128),
    ]

# Win32 Constants
# ENUM_CURRENT_SETTINGS = -1
# ENUM_REGISTRY_SETTINGS = -2
# DM_DISPLAYORIENTATION = 0x00000080
# DM_PELSWIDTH = 0x00080000
# DM_PELSHEIGHT = 0x00100000
# DMDO_DEFAULT = 0
# DMDO_90 = 1
# DMDO_180 = 2
# DMDO_270 = 3
# CDS_UPDATEREGISTRY = 0x00000001
# CDS_TEST = 0x00000002
# CDS_FULLSCREEN = 0x00000004
# CDS_GLOBAL = 0x00000008
# CDS_SET_PRIMARY = 0x00000010
# CDS_RESET = 0x40000000
# CDS_NORESET = 0x10000000

def test_all():
    dev = r"\\.\DISPLAY1"
    
    # 1. Try EnumDisplaySettings with ENUM_REGISTRY_SETTINGS (-2) vs ENUM_CURRENT_SETTINGS (-1)
    for enum_idx in [-1, -2]:
        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)
        res = ctypes.windll.user32.EnumDisplaySettingsW(dev, enum_idx, ctypes.byref(dm))
        print(f"Enum {enum_idx}: res={res}, fields={hex(dm.dmFields)}, orient={dm.dmDisplayOrientation}, w={dm.dmPelsWidth}, h={dm.dmPelsHeight}, freq={dm.dmDisplayFrequency}")

    # 2. Check all modes supported by DISPLAY1
    modes = []
    idx = 0
    while True:
        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)
        if not ctypes.windll.user32.EnumDisplaySettingsW(dev, idx, ctypes.byref(dm)):
            break
        if dm.dmDisplayOrientation != 0:
            modes.append((dm.dmPelsWidth, dm.dmPelsHeight, dm.dmDisplayOrientation, dm.dmDisplayFrequency))
        idx += 1
    print(f"Total modes enumerated: {idx}. Non-zero orientation modes: {len(modes)}")
    if modes:
        print("Sample rotated modes:", modes[:5])

    # 3. Test ChangeDisplaySettingsExW with various combinations
    dm = DEVMODEW()
    dm.dmSize = ctypes.sizeof(DEVMODEW)
    ctypes.windll.user32.EnumDisplaySettingsW(dev, -1, ctypes.byref(dm))
    
    # Try just dmDisplayOrientation
    dm.dmDisplayOrientation = 2 # 180 deg
    
    # Combination A: dmFields = DM_DISPLAYORIENTATION only
    dm.dmFields = 0x00000080
    r1 = ctypes.windll.user32.ChangeDisplaySettingsExW(dev, ctypes.byref(dm), None, 2, None) # CDS_TEST
    print(f"Test A (only DM_DISPLAYORIENTATION): {r1}")

    # Combination B: dmFields = DM_DISPLAYORIENTATION | DM_PELSWIDTH | DM_PELSHEIGHT
    dm.dmFields = 0x00000080 | 0x00080000 | 0x00100000
    r2 = ctypes.windll.user32.ChangeDisplaySettingsExW(dev, ctypes.byref(dm), None, 2, None)
    print(f"Test B (orient + width + height): {r2}")

    # Combination C: keep original dmFields and add DM_DISPLAYORIENTATION
    dm_c = DEVMODEW()
    dm_c.dmSize = ctypes.sizeof(DEVMODEW)
    ctypes.windll.user32.EnumDisplaySettingsW(dev, -1, ctypes.byref(dm_c))
    dm_c.dmDisplayOrientation = 2
    dm_c.dmFields |= 0x00000080
    r3 = ctypes.windll.user32.ChangeDisplaySettingsExW(dev, ctypes.byref(dm_c), None, 2, None)
    print(f"Test C (original dmFields |= 0x80): {r3}")

    # Combination D: device = None (primary screen)
    r4 = ctypes.windll.user32.ChangeDisplaySettingsExW(None, ctypes.byref(dm_c), None, 2, None)
    print(f"Test D (device = None): {r4}")

    # Combination E: ChangeDisplaySettingsW (non-Ex)
    r5 = ctypes.windll.user32.ChangeDisplaySettingsW(ctypes.byref(dm_c), 2)
    print(f"Test E (ChangeDisplaySettingsW CDS_TEST): {r5}")

    # Combination F: What if CDS_UPDATEREGISTRY (1) instead of CDS_TEST (2)?
    # Some graphics drivers (like NVIDIA desktop drivers) DO NOT support CDS_TEST (CDS_TEST returns -1)
    # but actual apply (0 or CDS_UPDATEREGISTRY) works, OR CDS_RESET (0x40000000)!
    # Let's test with CDS_UPDATEREGISTRY | CDS_RESET
    r6 = ctypes.windll.user32.ChangeDisplaySettingsExW(dev, ctypes.byref(dm_c), None, 0x00000001, None)
    print(f"Test F (CDS_UPDATEREGISTRY): {r6}")
    if r6 == 0:
        print("SUCCESS with CDS_UPDATEREGISTRY! Restoring...")
        dm_c.dmDisplayOrientation = 0
        ctypes.windll.user32.ChangeDisplaySettingsExW(dev, ctypes.byref(dm_c), None, 0x00000001, None)

if __name__ == "__main__":
    test_all()
