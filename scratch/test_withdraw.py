import tkinter as tk
import time

root = tk.Tk()
root.title("Main")

toplevel = tk.Toplevel(root)
toplevel.title("Toplevel Window")
toplevel.update()

hwnd1 = int(toplevel.wm_frame(), 16)
print(f"Initial HWND: {hwnd1}")

toplevel.withdraw()
toplevel.update()

toplevel.deiconify()
toplevel.update()

hwnd2 = int(toplevel.wm_frame(), 16)
print(f"HWND after deiconify: {hwnd2}")
print(f"Are they equal? {hwnd1 == hwnd2}")

root.destroy()
