import tkinter as tk
import ctypes
import math
import random
import time

class TestGhost:
    def __init__(self, root):
        self.root = root
        self.sw = root.winfo_screenwidth()
        self.sh = root.winfo_screenheight()
        
        self.gx = self.sw * 0.5
        self.gy = self.sh * 0.3
        self.vx = 2.0
        self.vy = 1.5
        self.target_mx = self.gx
        self.target_my = self.gy
        
        self.state = "WANDER" # WANDER, CHASE, JUMPSCARE
        self.state_timer = 0
        self.phase = 0.0
        self.ectoplasm = []
        self.sound_waves = []
        self.jumpscare_scale = 1.0
        self.booh_text = ""
        
        print("TestGhost initialized for screen:", self.sw, self.sh)
        
    def tick(self, mx, my):
        self.phase += 0.08
        self.state_timer += 1
        
        if self.state == "WANDER":
            # Wander around smoothly
            self.gx += math.sin(self.phase * 0.7) * 5.0 + self.vx
            self.gy += math.cos(self.phase * 0.9) * 4.0 + self.vy
            
            # Bounce off screen borders
            if self.gx < 80: self.vx = abs(self.vx)
            if self.gx > self.sw - 80: self.vx = -abs(self.vx)
            if self.gy < 80: self.vy = abs(self.vy)
            if self.gy > self.sh - 120: self.vy = -abs(self.vy)
            
            # Chance to drop green ectoplasm slime
            if random.random() < 0.05 and len(self.ectoplasm) < 10:
                self.ectoplasm.append({"x": self.gx + random.uniform(-20, 20), "y": self.gy + 35, "r": random.uniform(8, 16), "drip": 0.0, "life": 1.0})
                
            # After 4-6 seconds, switch to CHASE
            if self.state_timer > 150:
                self.state = "CHASE"
                self.state_timer = 0
                
        elif self.state == "CHASE":
            # Swoop towards mouse cursor
            dx = mx - self.gx
            dy = my - self.gy
            dist = math.hypot(dx, dy)
            if dist > 30:
                self.gx += (dx / dist) * 12.0
                self.gy += (dy / dist) * 12.0
            else:
                self.state = "JUMPSCARE"
                self.state_timer = 0
                self.jumpscare_scale = 1.8
                self.booh_text = random.choice(["BOOOOUH ! 👻⚡", "ATTRAPÉ ! 👻💥", "OUUUH ! 👻✨"])
                # Spook repulsion
                return True # repels cursor!
                
            if self.state_timer > 90: # give up after 3s
                self.state = "WANDER"
                self.state_timer = 0
                
        elif self.state == "JUMPSCARE":
            self.jumpscare_scale = max(1.0, self.jumpscare_scale - 0.06)
            if self.state_timer > 25:
                self.state = "WANDER"
                self.state_timer = 0
                self.booh_text = ""
                self.vx = random.choice([-3, 3])
                self.vy = random.choice([-2, 2])
                
        # Update ectoplasm
        new_ecto = []
        for e in self.ectoplasm:
            e["drip"] += 0.8
            e["life"] -= 0.015
            if e["life"] > 0:
                new_ecto.append(e)
        self.ectoplasm = new_ecto
        return False

def test():
    root = tk.Tk()
    root.withdraw()
    g = TestGhost(root)
    # Simulate 300 ticks
    for i in range(300):
        repel = g.tick(500, 400)
        if repel:
            print(f"Tick {i}: JUMPSCARE & REPEL TRIGGERED!")
    print("Ghost state machine test completed successfully!")
    root.destroy()

if __name__ == "__main__":
    test()
