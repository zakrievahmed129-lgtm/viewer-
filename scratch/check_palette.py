from PIL import Image
from collections import Counter

img = Image.open(r"assets/monkey/monkey_volume_spritesheet.png").convert("RGBA")
colors = Counter(img.getdata())
print(f"Total unique colors: {len(colors)}")
for c, cnt in colors.most_common(10):
    print(f"  Color {c}: count={cnt}")
