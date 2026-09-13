import ctypes
from ctypes import wintypes
import time
import threading

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, ctypes.POINTER(MSLLHOOKSTRUCT))

last_phys_x = None
last_phys_y = None
invert_active = True

def mouse_callback(nCode, wParam, lParam):
    global last_phys_x, last_phys_y, invert_active
    try:
        if nCode >= 0 and lParam and invert_active:
            info = lParam.contents
            # Ignore injected events
            if not (info.flags & 0x00000001):
                cur_x, cur_y = info.pt.x, info.pt.y
                if last_phys_x is not None and last_phys_y is not None:
                    dx = cur_x - last_phys_x
                    dy = cur_y - last_phys_y
                    if dx != 0 or dy != 0:
                        # Invert delta
                        # Get actual current cursor pos
                        cur_pt = POINT()
                        ctypes.windll.user32.GetCursorPos(ctypes.byref(cur_pt))
                        inv_x = cur_pt.x - dx
                        inv_y = cur_pt.y - dy
                        ctypes.windll.user32.SetCursorPos(inv_x, inv_y)
                        last_phys_x = cur_x
                        last_phys_y = cur_y
                        return 1
                last_phys_x = cur_x
                last_phys_y = cur_y
    except Exception as e:
        pass
    return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)

def test():
    hook_proc = HOOKPROC(mouse_callback)
    hook = ctypes.windll.user32.SetWindowsHookExW(14, hook_proc, ctypes.windll.kernel32.GetModuleHandleW(None), 0)
    print("Hook installed:", hook)
    
    # Run message loop for 1.5 seconds
    t_end = time.time() + 1.5
    msg = wintypes.MSG()
    while time.time() < t_end:
        while ctypes.windll.user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1):
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.01)
        
    ctypes.windll.user32.UnhookWindowsHookEx(hook)
    print("Hook uninstalled successfully!")

if __name__ == "__main__":
    test()
