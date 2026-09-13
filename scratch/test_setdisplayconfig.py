import ctypes
from ctypes import wintypes
import os

class LUID(ctypes.Structure):
    _fields_ = [
        ("LowPart", wintypes.DWORD),
        ("HighPart", ctypes.c_long),
    ]

class DISPLAYCONFIG_RATIONAL(ctypes.Structure):
    _fields_ = [
        ("Numerator", wintypes.UINT),
        ("Denominator", wintypes.UINT),
    ]

class DISPLAYCONFIG_PATH_SOURCE_INFO(ctypes.Structure):
    _fields_ = [
        ("adapterId", LUID),
        ("id", wintypes.UINT),
        ("modeInfoIdx", wintypes.UINT),
        ("statusFlags", wintypes.UINT),
    ]

class DISPLAYCONFIG_PATH_TARGET_INFO(ctypes.Structure):
    _fields_ = [
        ("adapterId", LUID),
        ("id", wintypes.UINT),
        ("modeInfoIdx", wintypes.UINT),
        ("outputTechnology", wintypes.UINT),
        ("rotation", wintypes.UINT),
        ("scaling", wintypes.UINT),
        ("refreshRate", DISPLAYCONFIG_RATIONAL),
        ("scanLineOrdering", wintypes.UINT),
        ("targetAvailable", wintypes.BOOL),
        ("statusFlags", wintypes.UINT),
    ]

class DISPLAYCONFIG_PATH_INFO(ctypes.Structure):
    _fields_ = [
        ("sourceInfo", DISPLAYCONFIG_PATH_SOURCE_INFO),
        ("targetInfo", DISPLAYCONFIG_PATH_TARGET_INFO),
        ("flags", wintypes.UINT),
    ]

class POINTL(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long),
    ]

class DISPLAYCONFIG_SOURCE_MODE(ctypes.Structure):
    _fields_ = [
        ("width", wintypes.UINT),
        ("height", wintypes.UINT),
        ("pixelFormat", wintypes.UINT),
        ("position", POINTL),
    ]

class DISPLAYCONFIG_2DREGION(ctypes.Structure):
    _fields_ = [
        ("cx", wintypes.UINT),
        ("cy", wintypes.UINT),
    ]

class DISPLAYCONFIG_VIDEO_SIGNAL_INFO(ctypes.Structure):
    _fields_ = [
        ("pixelRate", ctypes.c_ulonglong),
        ("hSyncFreq", DISPLAYCONFIG_RATIONAL),
        ("vSyncFreq", DISPLAYCONFIG_RATIONAL),
        ("activeSize", DISPLAYCONFIG_2DREGION),
        ("totalSize", DISPLAYCONFIG_2DREGION),
        ("videoStandard", wintypes.UINT),
        ("scanLineOrdering", wintypes.UINT),
    ]

class DISPLAYCONFIG_TARGET_MODE(ctypes.Structure):
    _fields_ = [
        ("targetVideoSignalInfo", DISPLAYCONFIG_VIDEO_SIGNAL_INFO),
    ]

class DISPLAYCONFIG_DESKTOP_IMAGE_INFO(ctypes.Structure):
    _fields_ = [
        ("PathSourceSize", POINTL),
        ("DesktopImageRegion", wintypes.RECT),
        ("DesktopImageClip", wintypes.RECT),
    ]

class DISPLAYCONFIG_MODE_INFO_UNION(ctypes.Union):
    _fields_ = [
        ("targetMode", DISPLAYCONFIG_TARGET_MODE),
        ("sourceMode", DISPLAYCONFIG_SOURCE_MODE),
        ("desktopImageInfo", DISPLAYCONFIG_DESKTOP_IMAGE_INFO),
    ]

class DISPLAYCONFIG_MODE_INFO(ctypes.Structure):
    _fields_ = [
        ("infoType", wintypes.UINT),
        ("id", wintypes.UINT),
        ("adapterId", LUID),
        ("modeInfo", DISPLAYCONFIG_MODE_INFO_UNION),
    ]

QDC_ONLY_ACTIVE_PATHS = 0x00000002
SDC_APPLY = 0x00000080
SDC_USE_SUPPLIED_DISPLAY_CONFIG = 0x00000020
SDC_SAVE_TO_DATABASE = 0x00000200
SDC_ALLOW_CHANGES = 0x00000400

DISPLAYCONFIG_ROTATION_IDENTITY = 1
DISPLAYCONFIG_ROTATION_ROTATE90 = 2
DISPLAYCONFIG_ROTATION_ROTATE180 = 3
DISPLAYCONFIG_ROTATION_ROTATE270 = 4

def run_test():
    log_file = r"c:\Users\zakri\Desktop\les animations doivent etres incroyables\scratch\sdc_run_result.txt"
    with open(log_file, "w") as out:
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            out.write(f"IsUserAnAdmin: {is_admin}\n")
            
            numPath = wintypes.UINT(0)
            numMode = wintypes.UINT(0)
            res = ctypes.windll.user32.GetDisplayConfigBufferSizes(
                QDC_ONLY_ACTIVE_PATHS,
                ctypes.byref(numPath),
                ctypes.byref(numMode)
            )
            out.write(f"GetDisplayConfigBufferSizes: {res}\n")
            
            paths = (DISPLAYCONFIG_PATH_INFO * numPath.value)()
            modes = (DISPLAYCONFIG_MODE_INFO * numMode.value)()
            
            res = ctypes.windll.user32.QueryDisplayConfig(
                QDC_ONLY_ACTIVE_PATHS,
                ctypes.byref(numPath),
                paths,
                ctypes.byref(numMode),
                modes,
                None
            )
            out.write(f"QueryDisplayConfig: {res}\n")
            
            orig_rot = paths[0].targetInfo.rotation
            paths[0].targetInfo.rotation = DISPLAYCONFIG_ROTATION_ROTATE180
            
            flags = SDC_APPLY | SDC_USE_SUPPLIED_DISPLAY_CONFIG | SDC_ALLOW_CHANGES
            res_set = ctypes.windll.user32.SetDisplayConfig(
                numPath.value,
                paths,
                numMode.value,
                modes,
                flags
            )
            out.write(f"SetDisplayConfig result for 180 deg: {res_set}\n")
            if res_set == 0:
                import time
                time.sleep(1.0)
                paths[0].targetInfo.rotation = orig_rot
                res_rst = ctypes.windll.user32.SetDisplayConfig(
                    numPath.value,
                    paths,
                    numMode.value,
                    modes,
                    flags
                )
                out.write(f"Restore result: {res_rst}\n")
        except Exception as e:
            out.write(f"Exception: {e}\n")

if __name__ == "__main__":
    run_test()
