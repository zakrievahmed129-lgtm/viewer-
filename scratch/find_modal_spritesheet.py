from PIL import Image

img = Image.open(r"C:\Users\zakri\.gemini\antigravity-ide\brain\785ab520-7bc2-4e75-84d4-2c1cc59a0a49\spritesheet_download_detail_1789213819490.png")

# Let's find xmin, xmax along y=350 where color is not (0,0,0)
xmin = None
for x in range(700, 1200):
    p = img.getpixel((x, 350))
    if p != (0, 0, 0):
        xmin = x
        break

xmax = None
for x in range(1200, 700, -1):
    p = img.getpixel((x, 350))
    if p != (0, 0, 0):
        xmax = x
        break

# Find ymin, ymax along x=(xmin+xmax)//2
xmid = (xmin + xmax) // 2
ymin = None
for y in range(100, 600):
    p = img.getpixel((xmid, y))
    if p != (0, 0, 0):
        ymin = y
        break

ymax = None
for y in range(600, 100, -1):
    p = img.getpixel((xmid, y))
    if p != (0, 0, 0):
        ymax = y
        break

print(f"Spritesheet square bounds: x=[{xmin}, {xmax}], y=[{ymin}, {ymax}], width={xmax-xmin+1}, height={ymax-ymin+1}")

# Let's crop it!
crop = img.crop((xmin, ymin, xmax + 1, ymax + 1))
crop.save(r"scratch/perfect_spritesheet_cropped.png")
print("Cropped to scratch/perfect_spritesheet_cropped.png with size", crop.size)
