import tkinter as tk
import ctypes
import time

ctypes.windll.user32.GetForegroundWindow.restype = ctypes.c_void_p
ctypes.windll.user32.GetAncestor.restype = ctypes.c_void_p
ctypes.windll.user32.GetAncestor.argtypes = [ctypes.c_void_p, ctypes.c_uint]

root = tk.Tk()
root.title("Main")

toplevel = tk.Toplevel(root)
toplevel.title("Toplevel Window")
text_widget = tk.Text(toplevel)
text_widget.pack()

def check_handles():
    toplevel.update()
    frame_hwnd = int(toplevel.wm_frame(), 16)
    
    # Wait a bit so user can focus text widget
    print("Focus the text widget now...")
    time.sleep(3)
    
    fore_hwnd = ctypes.windll.user32.GetForegroundWindow()
    ancestor_hwnd = ctypes.windll.user32.GetAncestor(fore_hwnd, 2) # GA_ROOT
    
    print(f"toplevel.wm_frame(): {toplevel.wm_frame()} -> {frame_hwnd}")
    print(f"GetForegroundWindow(): {fore_hwnd}")
    print(f"GetAncestor(fore, GA_ROOT): {ancestor_hwnd}")
    print(f"Match wm_frame == GetForegroundWindow? {frame_hwnd == fore_hwnd}")
    print(f"Match wm_frame == GetAncestor? {frame_hwnd == ancestor_hwnd}")
    
    root.destroy()

root.after(500, check_handles)
root.mainloop()
