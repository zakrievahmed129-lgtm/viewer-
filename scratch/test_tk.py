import tkinter as tk
import ctypes
import math
import random
import time

def test():
    root = tk.Tk()
    root.withdraw()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    print("Screen size:", sw, sh)
    root.destroy()

if __name__ == "__main__":
    test()
