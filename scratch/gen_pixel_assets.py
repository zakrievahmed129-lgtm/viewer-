import base64
import os

with open(r"assets/monkey/monkey_volume_transparent.png", "rb") as f:
    monkey_b64 = base64.b64encode(f.read()).decode('ascii')

content = f'''# -*- coding: utf-8 -*-
"""
Module contenant les assets pixel art encodés en base64 pour garantir
une totale autonomie sans dépendre de fichiers externes lors de la compilation .exe.
"""
import io
import os
from PIL import Image, ImageTk

# Spritesheet singe farceur Retro Diffusion (256x256, 16 frames de 64x64, 4x4)
MONKEY_SPRITESHEET_B64 = """{monkey_b64}"""

def get_monkey_frames_pil(scale=4, bg_hex="#010101"):
    """
    Retourne les 16 frames PIL RGBA compositées sur la couleur de transparence Tkinter.
    """
    frame_w = 64
    frame_h = 64
    target_size = (frame_w * scale, frame_h * scale)
    
    # Parse hex color
    bg_hex = bg_hex.lstrip('#')
    bg_rgb = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
    
    # Check if files exist on disk first, otherwise decode base64
    frames = []
    frames_dir = os.path.join(os.path.dirname(__file__), "assets", "monkey", "frames")
    
    loaded_from_disk = False
    if os.path.exists(frames_dir):
        disk_frames = [os.path.join(frames_dir, f"frame_{{i:02d}}.png") for i in range(16)]
        if all(os.path.exists(p) for p in disk_frames):
            try:
                for p in disk_frames:
                    img_rgba = Image.open(p).convert("RGBA")
                    scaled = img_rgba.resize(target_size, Image.NEAREST)
                    bg = Image.new("RGBA", target_size, (*bg_rgb, 255))
                    bg.paste(scaled, (0, 0), scaled)
                    frames.append(bg)
                loaded_from_disk = True
            except Exception:
                frames = []
                loaded_from_disk = False
                
    if not loaded_from_disk:
        raw_data = base64.b64decode(MONKEY_SPRITESHEET_B64)
        sheet = Image.open(io.BytesIO(raw_data)).convert("RGBA")
        for row in range(4):
            for col in range(4):
                box = (col * frame_w, row * frame_h, (col + 1) * frame_w, (row + 1) * frame_h)
                frame = sheet.crop(box)
                scaled = frame.resize(target_size, Image.NEAREST)
                bg = Image.new("RGBA", target_size, (*bg_rgb, 255))
                bg.paste(scaled, (0, 0), scaled)
                frames.append(bg)
                
    return frames

def get_monkey_photoimages(scale=4, bg_hex="#010101"):
    """
    Retourne les 16 frames sous forme de ImageTk.PhotoImage prêtes pour Tkinter Canvas.
    """
    pil_frames = get_monkey_frames_pil(scale=scale, bg_hex=bg_hex)
    return [ImageTk.PhotoImage(f) for f in pil_frames]
'''

with open("pixel_assets.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Generated pixel_assets.py successfully!")
