from PIL import Image

img = Image.open(r"C:\Users\zakri\.gemini\antigravity-ide\brain\785ab520-7bc2-4e75-84d4-2c1cc59a0a49\spritesheet_view_1789213528889.png")

# Find horizontal bounds of the canvas
# The background outside is dark (r < 50, g < 50, b < 50)
# Inside canvas is (192, 192, 192) or sprite pixels
xmin = None
for x in range(500, 700):
    r, g, b, *rest = img.getpixel((x, 300))
    if r > 100 and g > 100 and b > 100:
        xmin = x
        break

xmax = None
for x in range(1500, 1300, -1):
    r, g, b, *rest = img.getpixel((x, 300))
    if r > 100 and g > 100 and b > 100:
        xmax = x
        break

ymin = None
for y in range(50, 200):
    r, g, b, *rest = img.getpixel((800, y))
    if r > 100 and g > 100 and b > 100:
        ymin = y
        break

ymax = None
for y in range(940, 700, -1):
    r, g, b, *rest = img.getpixel((800, y))
    if r > 100 and g > 100 and b > 100:
        ymax = y
        break

print(f"Canvas square bounds: x=[{xmin}, {xmax}], y=[{ymin}, {ymax}], width={xmax-xmin+1}, height={ymax-ymin+1}")

crop = img.crop((xmin, ymin, xmax + 1, ymax + 1))
crop.save(r"scratch/main_canvas_spritesheet.png")
print("Saved scratch/main_canvas_spritesheet.png with size", crop.size)
