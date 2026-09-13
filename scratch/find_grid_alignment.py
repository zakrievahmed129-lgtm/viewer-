from PIL import Image

img = Image.open(r"C:\Users\zakri\.gemini\antigravity-ide\brain\785ab520-7bc2-4e75-84d4-2c1cc59a0a49\spritesheet_view_1789213528889.png")

# Check x=623:
print("At (622, 106):", img.getpixel((622, 106)))
print("At (623, 106):", img.getpixel((623, 106)))
print("At (623, 105):", img.getpixel((623, 105)))

# So x0 = 623, y0 = 106!
# Now let's find the bottom and right edge!
for x in range(1300, 1500):
    p_curr = img.getpixel((x, 200))
    p_next = img.getpixel((x + 1, 200))
    if p_curr[0] > 100 and p_next[0] < 50:
        print(f"Right edge at x={x}")
        break

for y in range(800, 940):
    p_curr = img.getpixel((700, y))
    p_next = img.getpixel((700, y + 1))
    if p_curr[0] > 100 and p_next[0] < 50:
        print(f"Bottom edge at y={y}")
        break
