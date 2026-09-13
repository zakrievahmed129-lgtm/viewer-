import ctypes
from ctypes import wintypes

class DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128),
    ]

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

def inspect():
    i = 0
    while True:
        dd = DISPLAY_DEVICEW()
        dd.cb = ctypes.sizeof(DISPLAY_DEVICEW)
        res = ctypes.windll.user32.EnumDisplayDevicesW(None, i, ctypes.byref(dd), 0)
        if not res:
            break
        print(f"Device {i}: Name='{dd.DeviceName}', String='{dd.DeviceString}', StateFlags={hex(dd.StateFlags)}")
        
        # Check if active / primary (DISPLAY_DEVICE_ATTACHED_TO_DESKTOP = 0x1, DISPLAY_DEVICE_PRIMARY_DEVICE = 0x4)
        if dd.StateFlags & 0x1:
            dm = DEVMODEW()
            dm.dmSize = ctypes.sizeof(DEVMODEW)
            res_settings = ctypes.windll.user32.EnumDisplaySettingsW(dd.DeviceName, -1, ctypes.byref(dm))
            print(f"  EnumDisplaySettingsW({dd.DeviceName}, ENUM_CURRENT_SETTINGS): {res_settings}")
            if res_settings:
                print(f"  Res: {dm.dmPelsWidth}x{dm.dmPelsHeight}, Orient: {dm.dmDisplayOrientation}, Freq: {dm.dmDisplayFrequency}")
                
                # Test ChangeDisplaySettingsExW with CDS_TEST
                # Test 180 degrees (dmDisplayOrientation = 2)
                dm.dmDisplayOrientation = 2
                # In landscape 0 -> 180: width and height DO NOT change!
                dm.dmFields |= 0x00000080 # DM_DISPLAYORIENTATION
                test_res = ctypes.windll.user32.ChangeDisplaySettingsExW(dd.DeviceName, ctypes.byref(dm), None, 2, None) # CDS_TEST = 2
                print(f"  CDS_TEST on {dd.DeviceName} for 180 deg: {test_res}")
                
                # Test with 0 (CDS_FULLSCREEN / CDS_RESET)
                # CDS_UPDATEREGISTRY = 1
                # CDS_RESET = 0x40000000
                test_res_0 = ctypes.windll.user32.ChangeDisplaySettingsExW(dd.DeviceName, ctypes.byref(dm), None, 0, None)
                print(f"  ChangeDisplaySettingsExW with 0: {test_res_0}")
                if test_res_0 == 0:
                    # restore immediately
                    dm.dmDisplayOrientation = 0
                    ctypes.windll.user32.ChangeDisplaySettingsExW(dd.DeviceName, ctypes.byref(dm), None, 0, None)
                    print("  Successfully tested and restored 180 deg rotation!")

        i += 1

if __name__ == "__main__":
    inspect()
