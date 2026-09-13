import os
import sys
import time
import ctypes
import tkinter as tk
from PIL import Image, ImageTk

# Virtual key codes
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_VOLUME_MUTE = 0xAD

def lower_volume():
    """Press volume down key to trigger native Windows volume reduction"""
    ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
    time.sleep(0.005)
    ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)

class PixelMonkeyOverlay:
    def __init__(self, root, scale=4):
        self.root = root
        self.scale = scale
        self.frame_size = 64 * scale # 256x256
        self.transparent_color = "#010101" # Unique color key for transparency
        
        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-transparentcolor', self.transparent_color)
        self.window.config(bg=self.transparent_color)
        
        # Position at bottom-right above taskbar
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        self.x = sw - self.frame_size - 80
        self.y = sh - self.frame_size - 100
        self.window.geometry(f"{self.frame_size}x{self.frame_size}+{self.x}+{self.y}")
        
        self.canvas = tk.Canvas(
            self.window,
            width=self.frame_size,
            height=self.frame_size,
            bg=self.transparent_color,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Load and prepare frames
        self.frames = []
        frames_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "monkey", "frames")
        if not os.path.exists(frames_dir):
            frames_dir = r"assets\monkey\frames"
            
        print(f"Loading frames from {frames_dir}...")
        for i in range(16):
            fpath = os.path.join(frames_dir, f"frame_{i:02d}.png")
            img_rgba = Image.open(fpath).convert("RGBA")
            # Resize with NEAREST for sharp pixel art
            img_scaled = img_rgba.resize((self.frame_size, self.frame_size), Image.NEAREST)
            
            # Composite onto transparent_color background
            bg_img = Image.new("RGBA", (self.frame_size, self.frame_size), (1, 1, 1, 255))
            bg_img.paste(img_scaled, (0, 0), img_scaled)
            photo = ImageTk.PhotoImage(bg_img)
            self.frames.append(photo)
            
        print(f"Loaded {len(self.frames)} frames at {self.frame_size}x{self.frame_size}px")
        
        self.current_frame = 0
        self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.frames[0])
        
        self.window.bind("<Escape>", lambda e: self.close())
        self.running = True
        self.animate()
        
    def animate(self):
        if not self.running:
            return
            
        # Update image
        self.canvas.itemconfig(self.image_id, image=self.frames[self.current_frame])
        
        # Volume manipulation during slider pull (frames 3 to 11)
        if 3 <= self.current_frame <= 11:
            lower_volume()
            lower_volume()
            
        # Frame delay:
        # Frames 0-2 (anticipation): 120ms
        # Frames 3-11 (pulling down): 100ms
        # Frames 12-15 (laughing triumphantly): 200ms
        delay = 100
        if self.current_frame >= 12:
            delay = 220
        elif self.current_frame < 3:
            delay = 140
            
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.root.after(delay, self.animate)
        
    def close(self):
        self.running = False
        try:
            self.window.destroy()
        except:
            pass

if __name__ == "__main__":
    print("Testing Pixel Monkey Overlay...")
    root = tk.Tk()
    root.withdraw()
    overlay = PixelMonkeyOverlay(root, scale=4)
    root.bind("<Escape>", lambda e: root.destroy())
    
    # Run for 10 seconds then close in test
    root.after(10000, root.destroy)
    root.mainloop()
    print("Test finished.")
