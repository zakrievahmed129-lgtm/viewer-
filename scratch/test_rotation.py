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

def test():
    dm = DEVMODEW()
    dm.dmSize = ctypes.sizeof(DEVMODEW)
    print("DEVMODEW size:", ctypes.sizeof(DEVMODEW))
    success = ctypes.windll.user32.EnumDisplaySettingsW(None, -1, ctypes.byref(dm))
    print("EnumDisplaySettingsW success:", success)
    if not success:
        print("GetLastError:", ctypes.GetLastError())
        return
    print(f"Device: {dm.dmDeviceName}, Pels: {dm.dmPelsWidth}x{dm.dmPelsHeight}, Orientation: {dm.dmDisplayOrientation}, Fields: {hex(dm.dmFields)}")
    
    # Test rotate 2
    # DISP_CHANGE_SUCCESSFUL = 0
    # DISP_CHANGE_RESTART = 1
    # DISP_CHANGE_FAILED = -1
    # DISP_CHANGE_BADMODE = -2
    # DISP_CHANGE_NOTUPDATED = -3
    # DISP_CHANGE_BADFLAGS = -4
    # DISP_CHANGE_BADPARAM = -5
    dm.dmDisplayOrientation = 2
    dm.dmFields = 0x00800000 | 0x00080000 | 0x00100000 # DM_DISPLAYORIENTATION (0x80) | DM_PELSWIDTH (0x80000) | DM_PELSHEIGHT (0x100000)
    # Note: DM_DISPLAYORIENTATION in wingdi.h is 0x00000080L !! NOT 0x00800000!
    # Let's check DM_DISPLAYORIENTATION value in Windows SDK!
    print("Fields used in ghost_script:", hex(dm.dmFields))
    res = ctypes.windll.user32.ChangeDisplaySettingsW(ctypes.byref(dm), 0) # CDS_TEST = 2 or CDS_UPDATEREGISTRY = 1
    print("ChangeDisplaySettingsW result with 0:", res)

    # Let's check proper constants
    # DM_DISPLAYORIENTATION = 0x00000080
    # DM_PELSWIDTH = 0x00080000
    # DM_PELSHEIGHT = 0x00100000
    dm.dmFields = 0x00000080 | 0x00080000 | 0x00100000
    res_proper = ctypes.windll.user32.ChangeDisplaySettingsW(ctypes.byref(dm), 2) # CDS_TEST = 2
    print("ChangeDisplaySettingsW CDS_TEST with proper DM_DISPLAYORIENTATION (0x80):", res_proper)

    # Restore to normal
    dm.dmDisplayOrientation = 0
    res_restore = ctypes.windll.user32.ChangeDisplaySettingsW(ctypes.byref(dm), 0)
    print("Restore result:", res_restore)

if __name__ == "__main__":
    test()
