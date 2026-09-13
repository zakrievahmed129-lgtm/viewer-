import tkinter as tk
import math
import random
import time

def test_render():
    root = tk.Tk()
    root.title("Test All Upgraded Cartoons")
    root.geometry("1000x800")
    root.configure(bg="#1e293b")
    
    canvas = tk.Canvas(root, width=1000, height=800, bg="#0f172a", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    # 1. Test Ghost with glowing tail, face, and ectoplasm
    gx, gy = 200, 200
    phase = 1.2
    # Ethereal aura
    for r in range(45, 15, -10):
        canvas.create_oval(gx - r, gy - r, gx + r, gy + r, fill="", outline="#38bdf8", width=2)
    # Ghost body
    pts = []
    for deg in range(0, 180, 15):
        rad = math.radians(deg)
        pts.append((gx + math.cos(rad) * 35, gy - 20 - math.sin(rad) * 35))
    pts.append((gx - 35, gy + 30))
    for step in range(5):
        tx = gx - 35 + step * 14
        wave = math.sin(phase * 3 + step) * 12
        pts.append((tx + 7, gy + 45 + wave))
    pts.append((gx + 35, gy + 30))
    canvas.create_polygon(pts, fill="#f8fafc", outline="#94a3b8", width=3, smooth=True)
    # Eyes & mouth
    canvas.create_oval(gx - 18, gy - 25, gx - 4, gy - 7, fill="#0f172a", outline="")
    canvas.create_oval(gx - 14, gy - 22, gx - 8, gy - 16, fill="#ffffff", outline="")
    canvas.create_oval(gx + 4, gy - 25, gx + 18, gy - 7, fill="#0f172a", outline="")
    canvas.create_oval(gx + 8, gy - 22, gx + 14, gy - 16, fill="#ffffff", outline="")
    canvas.create_oval(gx - 10, gy - 2, gx + 10, gy + 18, fill="#0f172a", outline="#94a3b8", width=2)
    canvas.create_text(gx, gy - 55, text="BOOOOUH ! 👻⚡", font=("Impact", 14, "bold"), fill="#38bdf8")
    
    # 2. Test Rotate Technician & Machinery
    cx, cy = 600, 250
    # Hazard plate
    canvas.create_rectangle(cx - 70, cy + 40, cx + 70, cy + 95, fill="#1e293b", outline="#0f172a", width=3)
    for h in range(-60, 60, 20):
        canvas.create_polygon([(cx + h, cy + 42), (cx + h + 10, cy + 42), (cx + h - 5, cy + 93), (cx + h - 15, cy + 93)], fill="#facc15", outline="")
    canvas.create_text(cx, cy + 68, text="BASCULE 180°", font=("Impact", 12, "bold"), fill="#ffffff")
    # Gears
    for ga in range(6):
        a = ga * math.pi / 3.0
        canvas.create_line(cx - 50, cy + 20, cx - 50 + math.cos(a) * 22, cy + 20 + math.sin(a) * 22, fill="#f59e0b", width=6)
    canvas.create_oval(cx - 65, cy + 5, cx - 35, cy + 35, fill="#d97706", outline="#78350f", width=2)
    # Lever
    canvas.create_line(cx, cy + 40, cx - 40, cy - 30, fill="#cbd5e1", width=9, capstyle=tk.ROUND)
    canvas.create_oval(cx - 52, cy - 42, cx - 28, cy - 18, fill="#ef4444", outline="#991b1b", width=3)
    # Technician
    tx, ty = cx + 20, cy - 20
    canvas.create_oval(tx - 22, ty - 35, tx + 22, ty + 25, fill="#2563eb", outline="#1e3a8a", width=3) # overalls
    canvas.create_oval(tx - 24, ty - 55, tx + 24, ty - 25, fill="#fed7aa", outline="#c2410c", width=2) # face
    canvas.create_arc(tx - 28, ty - 68, tx + 28, ty - 35, start=0, extent=180, fill="#facc15", outline="#854d0e", width=3) # helmet
    canvas.create_oval(tx - 6, ty - 66, tx + 6, ty - 54, fill="#ffffff", outline="#ca8a04", width=2) # lamp
    canvas.create_text(tx + 25, ty - 45, text="💦", font=("Segoe UI Emoji", 14))
    
    # 3. Test Puller (Souris Dérivante)
    px, py = 250, 600
    # Muscular body leaning
    canvas.create_line(px - 10, py + 10, px - 60, py + 45, fill="#1e3a8a", width=14, capstyle=tk.ROUND) # back leg
    canvas.create_line(px + 5, py + 10, px - 15, py + 45, fill="#2563eb", width=14, capstyle=tk.ROUND) # front leg
    canvas.create_oval(px - 28, py - 35, px + 22, py + 15, fill="#ea580c", outline="#9a3412", width=3) # torso
    canvas.create_oval(px - 18, py - 55, px + 22, py - 20, fill="#fed7aa", outline="#c2410c", width=3) # head
    # Red headband with flapping ribbons
    canvas.create_line(px - 20, py - 46, px + 24, py - 46, fill="#ef4444", width=6)
    canvas.create_line(px - 20, py - 46, px - 45, py - 52, fill="#dc2626", width=4)
    canvas.create_line(px - 20, py - 46, px - 40, py - 38, fill="#dc2626", width=4)
    # Rope
    canvas.create_line(px + 10, py - 10, px + 120, py + 20, fill="#d97706", width=5, dash=(6, 2))
    canvas.create_text(px + 140, py + 25, text="🖱️", font=("Segoe UI Emoji", 18))
    canvas.create_text(px - 5, py - 70, text="HNNNGH! 💪💢", font=("Impact", 13, "bold"), fill="#f97316")
    
    # 4. Test Key Gremlin
    kx, ky = 700, 600
    # Purple body & ears
    canvas.create_polygon([(kx - 35, ky - 35), (kx - 65, ky - 55), (kx - 25, ky - 20)], fill="#a855f7", outline="#581c87", width=2)
    canvas.create_polygon([(kx + 35, ky - 35), (kx + 65, ky - 55), (kx + 25, ky - 20)], fill="#a855f7", outline="#581c87", width=2)
    canvas.create_oval(kx - 35, ky - 40, kx + 35, ky + 25, fill="#9333ea", outline="#581c87", width=3)
    # Cat eyes
    canvas.create_oval(kx - 22, ky - 25, kx - 6, ky - 5, fill="#facc15", outline="#713f12", width=2)
    canvas.create_line(kx - 14, ky - 25, kx - 14, ky - 5, fill="#0f172a", width=3)
    canvas.create_oval(kx + 6, ky - 25, kx + 22, ky - 5, fill="#facc15", outline="#713f12", width=2)
    canvas.create_line(kx + 14, ky - 25, kx + 14, ky - 5, fill="#0f172a", width=3)
    # Mini Keyboard
    canvas.create_rectangle(kx - 45, ky + 20, kx + 45, ky + 45, fill="#334155", outline="#0f172a", width=3)
    # Spring with bouncing key
    sx, sy = kx + 20, ky - 10
    canvas.create_line(sx, sy + 30, sx - 5, sy + 20, sx + 5, sy + 10, sx, sy, fill="#94a3b8", width=3)
    canvas.create_rectangle(sx - 15, sy - 25, sx + 15, sy, fill="#38bdf8", outline="#0284c7", width=2)
    canvas.create_text(sx, sy - 12, text="[A]", font=("Impact", 11, "bold"), fill="#ffffff")
    canvas.create_text(kx, ky - 65, text="HIHIHI ! ⌨️", font=("Impact", 13, "bold"), fill="#fde047")

    root.update()
    time.sleep(1.0)
    root.destroy()
    print("Render test completed successfully with 0 errors!")

if __name__ == "__main__":
    test_render()
