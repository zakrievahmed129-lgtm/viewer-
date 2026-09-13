import ctypes
from ctypes import wintypes
import test_setdisplayconfig as t

def test_flags():
    numPath = wintypes.UINT(0)
    numMode = wintypes.UINT(0)
    t.ctypes.windll.user32.GetDisplayConfigBufferSizes(
        t.QDC_ONLY_ACTIVE_PATHS,
        ctypes.byref(numPath),
        ctypes.byref(numMode)
    )
    paths = (t.DISPLAYCONFIG_PATH_INFO * numPath.value)()
    modes = (t.DISPLAYCONFIG_MODE_INFO * numMode.value)()
    t.ctypes.windll.user32.QueryDisplayConfig(
        t.QDC_ONLY_ACTIVE_PATHS,
        ctypes.byref(numPath),
        paths,
        ctypes.byref(numMode),
        modes,
        None
    )
    
    paths[0].targetInfo.rotation = t.DISPLAYCONFIG_ROTATION_ROTATE180
    
    test_combos = [
        ("SDC_APPLY | SDC_USE_SUPPLIED_DISPLAY_CONFIG", 0x00000080 | 0x00000020),
        ("SDC_APPLY | SDC_USE_SUPPLIED_DISPLAY_CONFIG | SDC_SAVE_TO_DATABASE", 0x00000080 | 0x00000020 | 0x00000200),
        ("SDC_APPLY | SDC_USE_SUPPLIED_DISPLAY_CONFIG | SDC_ALLOW_CHANGES", 0x00000080 | 0x00000020 | 0x00000400),
        ("SDC_APPLY | SDC_USE_SUPPLIED_DISPLAY_CONFIG | SDC_SAVE_TO_DATABASE | SDC_ALLOW_CHANGES", 0x00000080 | 0x00000020 | 0x00000200 | 0x00000400),
        ("SDC_APPLY | SDC_ALLOW_CHANGES", 0x00000080 | 0x00000400),
        ("SDC_VALIDATE", 0x00000040 | 0x00000020),
    ]
    
    for name, flg in test_combos:
        res = t.ctypes.windll.user32.SetDisplayConfig(
            numPath.value,
            paths,
            numMode.value,
            modes,
            flg
        )
        print(f"{name}: {res}")

if __name__ == "__main__":
    test_flags()
