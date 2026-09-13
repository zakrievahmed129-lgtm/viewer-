from PIL import Image

img = Image.open(r"C:\Users\zakri\.gemini\antigravity-ide\brain\785ab520-7bc2-4e75-84d4-2c1cc59a0a49\spritesheet_view_1789213528889.png")
w, h = img.size

# Let's inspect the row at y=300 from x=500 to x=1500
for x in range(500, 1500, 20):
    p = img.getpixel((x, 300))
    # print sample
# Find contiguous region where color is the canvas light grey background
# Let's see what the background color of the canvas actually is
bg = img.getpixel((700, 200))
print("Sample canvas bg at (700, 200):", bg)

# The canvas has a specific light grey color: around (200..220, 200..220, 200..220)
# Let's find the exact bounding box of the canvas square:
canvas_bg = bg[:3]

# Let's find left, right, top, bottom of the canvas square
# In Retro Diffusion, the canvas is centered in the workspace
# Let's find xmin where pixels at y=200 match canvas_bg
for x in range(300, 1500):
    diff = sum(abs(c1 - c2) for c1, c2 in zip(img.getpixel((x, 200))[:3], canvas_bg))
    if diff < 10:
        xmin = x
        break

for x in range(1600, 500, -1):
    diff = sum(abs(c1 - c2) for c1, c2 in zip(img.getpixel((x, 200))[:3], canvas_bg))
    if diff < 10:
        xmax = x
        break

for y in range(50, 900):
    diff = sum(abs(c1 - c2) for c1, c2 in zip(img.getpixel((xmin + 50, y))[:3], canvas_bg))
    if diff < 10:
        ymin = y
        break

for y in range(900, 50, -1):
    diff = sum(abs(c1 - c2) for c1, c2 in zip(img.getpixel((xmin + 50, y))[:3], canvas_bg))
    if diff < 10:
        ymax = y
        break

print(f"Precise canvas square: x=[{xmin}, {xmax}], y=[{ymin}, {ymax}], size={xmax-xmin+1}x{ymax-ymin+1}")
crop = img.crop((xmin, ymin, xmax + 1, ymax + 1))
crop.save(r"scratch/canvas_exact.png")
print("Saved scratch/canvas_exact.png")
