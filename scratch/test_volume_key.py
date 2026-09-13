import ctypes
import time

VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_VOLUME_MUTE = 0xAD

def press_key(vk):
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.01)
    ctypes.windll.user32.keybd_event(vk, 0, 2, 0) # KEYEVENTF_KEYUP = 2

print("Testing volume down key press...")
press_key(VK_VOLUME_DOWN)
print("Volume down key pressed successfully!")
