from PIL import Image

# Let's inspect main_canvas_spritesheet.png
img = Image.open(r"scratch/main_canvas_spritesheet.png")
w, h = img.size
print(f"main_canvas_spritesheet size: {w}x{h}")

# The spritesheet is a 4x4 grid.
# Retro Diffusion standard animation is 64x64 pixels per frame.
# In a 4x4 grid, the raw resolution is 256x256 pixels!
# On canvas, it is rendered at a scaled integer or float zoom.
# Let's check the size of each "pixel" (pixel block size)
# Look at the monkey's black outline pixels.
# Let's find common runs of identical color pixels along rows and columns.

from collections import Counter
runs_x = []
runs_y = []

for y in range(h):
    run = 1
    for x in range(1, w):
        if img.getpixel((x, y)) == img.getpixel((x - 1, y)):
            run += 1
        else:
            if run > 1:
                runs_x.append(run)
            run = 1

for x in range(w):
    run = 1
    for y in range(1, h):
        if img.getpixel((x, y)) == img.getpixel((x, y - 1)):
            run += 1
        else:
            if run > 1:
                runs_y.append(run)
            run = 1

print("Most common horizontal run lengths:", Counter(runs_x).most_common(10))
print("Most common vertical run lengths:", Counter(runs_y).most_common(10))
