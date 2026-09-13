import win32api, win32con

s = win32api.EnumDisplayDevices(None, 0)
dev = s.DeviceName
print("Testing on device:", dev)

flag_options = [
    ("0", 0),
    ("CDS_UPDATEREGISTRY", win32con.CDS_UPDATEREGISTRY), # 1
    ("CDS_TEST", win32con.CDS_TEST), # 2
    ("CDS_FULLSCREEN", win32con.CDS_FULLSCREEN), # 4
    ("CDS_GLOBAL", win32con.CDS_GLOBAL), # 8
    ("CDS_SET_PRIMARY", win32con.CDS_SET_PRIMARY), # 16
    ("CDS_RESET", win32con.CDS_RESET), # 0x40000000
    ("CDS_NORESET", win32con.CDS_NORESET), # 0x10000000
    ("CDS_UPDATEREGISTRY | CDS_RESET", win32con.CDS_UPDATEREGISTRY | win32con.CDS_RESET),
    ("CDS_GLOBAL | CDS_UPDATEREGISTRY", win32con.CDS_GLOBAL | win32con.CDS_UPDATEREGISTRY),
]

# Get current devmode
dm = win32api.EnumDisplaySettings(dev, win32con.ENUM_CURRENT_SETTINGS)
print(f"Current mode: {dm.PelsWidth}x{dm.PelsHeight}, Orient={dm.DisplayOrientation}, Freq={dm.DisplayFrequency}")

# Set to 180 degrees
dm.DisplayOrientation = win32con.DMDO_180
# Make sure fields has DM_DISPLAYORIENTATION
dm.Fields = dm.Fields | win32con.DM_DISPLAYORIENTATION

for name, flg in flag_options:
    res = win32api.ChangeDisplaySettingsEx(dev, dm, flg)
    print(f"Flag {name} ({hex(flg)}): {res}")
    if res == 0:
        print(f"SUCCESS with {name}!! Restoring...")
        dm.DisplayOrientation = win32con.DMDO_DEFAULT
        win32api.ChangeDisplaySettingsEx(dev, dm, flg)
        break
