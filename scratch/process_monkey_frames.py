import os
from PIL import Image

spritesheet_path = r"assets/monkey/monkey_volume_spritesheet.png"
output_dir = r"assets/monkey/frames"
os.makedirs(output_dir, exist_ok=True)

img = Image.open(spritesheet_path).convert("RGBA")
w, h = img.size

# Background color is exactly (202, 202, 202, 255)
BG_COLOR = (202, 202, 202, 255)

frame_w = 64
frame_h = 64

frames = []
for row in range(4):
    for col in range(4):
        box = (col * frame_w, row * frame_h, (col + 1) * frame_w, (row + 1) * frame_h)
        frame = img.crop(box)
        
        # Make transparent
        new_pixels = []
        for p in frame.getdata():
            if p[:3] == (202, 202, 202):
                new_pixels.append((0, 0, 0, 0))
            else:
                new_pixels.append(p)
        
        transparent_frame = Image.new("RGBA", (frame_w, frame_h))
        transparent_frame.putdata(new_pixels)
        
        idx = row * 4 + col
        frame_path = os.path.join(output_dir, f"frame_{idx:02d}.png")
        transparent_frame.save(frame_path)
        frames.append(transparent_frame)

print(f"Saved {len(frames)} transparent frames to {output_dir}")

# Create scaled spritesheet for preview
scaled_sheet = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
for row in range(4):
    for col in range(4):
        idx = row * 4 + col
        scaled = frames[idx].resize((frame_w * 2, frame_h * 2), Image.NEAREST)
        scaled_sheet.paste(scaled, (col * frame_w * 2, row * frame_h * 2))
scaled_sheet.save(r"assets/monkey/monkey_volume_transparent_2x.png")
print("Saved 2x scaled transparent spritesheet to assets/monkey/monkey_volume_transparent_2x.png")
