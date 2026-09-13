import tkinter as tk
import math
import random
from PIL import Image, ImageTk

# Test render drunk overlay frame
root = tk.Tk()
root.geometry("400x400")
root.configure(bg="#1e293b")

canvas = tk.Canvas(root, width=400, height=400, bg="#0f172a", highlightthickness=0)
canvas.pack(fill="both", expand=True)

mx = 200
my = 200
phase = 1.2
bubbles = []

# 1. ORBIT BEHIND
head_x = mx
head_y = my - 16
orbit_rx = 42.0
orbit_ry = 16.0
star_count = 5

for i in range(star_count):
    ang = phase * 1.8 + i * (2 * math.pi / star_count)
    sin_a = math.sin(ang)
    if sin_a < 0:
        sx = head_x + math.cos(ang) * orbit_rx
        sy = head_y + sin_a * orbit_ry
        scale = 0.75 + 0.25 * (sin_a + 1.0) / 2.0
        font_sz = max(8, int(13 * scale))
        sym = "⭐" if i % 2 == 0 else "💫"
        canvas.create_text(sx, sy, text=sym, font=("Segoe UI Emoji", font_sz))

# 2. CURSOR SOURIS QUI VACILLE
sway_angle = math.sin(phase * 1.5) * 26.0 + math.cos(phase * 0.7) * 10.0
sway_rad = math.radians(sway_angle)

base_pts = [
    (0, 0),
    (0, 28),
    (7, 21),
    (14, 32),
    (19, 30),
    (12, 18),
    (21, 18)
]
rot_pts = []
cos_r = math.cos(sway_rad)
sin_r = math.sin(sway_rad)
for px, py in base_pts:
    rx = mx + (px * cos_r - py * sin_r)
    ry = my + (px * sin_r + py * cos_r)
    rot_pts.append((rx, ry))

canvas.create_polygon(rot_pts, fill="#ffffff", outline="#000000", width=2.5)

cheek1_x = mx + (5 * cos_r - 14 * sin_r)
cheek1_y = my + (5 * sin_r + 14 * cos_r)
canvas.create_oval(cheek1_x - 4, cheek1_y - 3, cheek1_x + 4, cheek1_y + 3, fill="#fb7185", outline="")

eye_x = mx + (6 * cos_r - 8 * sin_r)
eye_y = my + (6 * sin_r + 8 * cos_r)
canvas.create_text(eye_x, eye_y, text="🌀", font=("Segoe UI Emoji", 8))

# 3. REALISTIC BOTTLE
gulp_bob = math.sin(phase * 4.0) * 3.5
bottle_tip_x = mx - 2
bottle_tip_y = my - 6 + gulp_bob

b_ang = math.radians(-44.0 + math.sin(phase * 2.0) * 6.0)
b_cos = math.cos(b_ang)
b_sin = math.sin(b_ang)

b_len = 82.0
b_w = 26.0

b_base_x = bottle_tip_x - b_cos * b_len
b_base_y = bottle_tip_y - b_sin * b_len

nx = -b_sin * (b_w / 2.0)
ny = b_cos * (b_w / 2.0)

neck_len = 28.0
neck_w = 11.0
nnx = -b_sin * (neck_w / 2.0)
nny = b_cos * (neck_w / 2.0)

neck_base_x = bottle_tip_x - b_cos * neck_len
neck_base_y = bottle_tip_y - b_sin * neck_len

body_pts = [
    (neck_base_x + nx, neck_base_y + ny),
    (b_base_x + nx, b_base_y + ny),
    (b_base_x - nx, b_base_y - ny),
    (neck_base_x - nx, neck_base_y - ny)
]
canvas.create_polygon(body_pts, fill="#78350f", outline="#451a03", width=2.5)
canvas.create_oval(b_base_x - 14, b_base_y - 14, b_base_x + 14, b_base_y + 14, fill="#451a03", outline="")

liq_base_x = b_base_x + b_cos * 6
liq_base_y = b_base_y + b_sin * 6
liq_pts = [
    (neck_base_x + nx*0.75, neck_base_y + ny*0.75),
    (liq_base_x + nx*0.75, liq_base_y + ny*0.75),
    (liq_base_x - nx*0.75, liq_base_y - ny*0.75),
    (neck_base_x - nx*0.75, neck_base_y - ny*0.75)
]
canvas.create_polygon(liq_pts, fill="#d97706", outline="")

lbl_cx = (neck_base_x + b_base_x) / 2.0
lbl_cy = (neck_base_y + b_base_y) / 2.0
canvas.create_oval(lbl_cx - 15, lbl_cy - 12, lbl_cx + 15, lbl_cy + 12, fill="#fef3c7", outline="#92400e", width=1.5)
canvas.create_text(lbl_cx, lbl_cy - 3, text="WHISKY", font=("Impact", 6, "bold"), fill="#78350f")
canvas.create_text(lbl_cx, lbl_cy + 4, text="80° ★", font=("Impact", 6, "bold"), fill="#b45309")

neck_pts = [
    (bottle_tip_x + nnx, bottle_tip_y + nny),
    (neck_base_x + nnx, neck_base_y + nny),
    (neck_base_x - nnx, neck_base_y - nny),
    (bottle_tip_x - nnx, bottle_tip_y - nny)
]
canvas.create_polygon(neck_pts, fill="#92400e", outline="#451a03", width=2)
collar_x = bottle_tip_x - b_cos * 10
collar_y = bottle_tip_y - b_sin * 10
canvas.create_line(collar_x + nnx*1.3, collar_y + nny*1.3, collar_x - nnx*1.3, collar_y - nny*1.3, fill="#f59e0b", width=3)

canvas.create_line(
    neck_base_x + nx*0.85, neck_base_y + ny*0.85,
    b_base_x + nx*0.85, b_base_y + ny*0.85,
    fill="#ffffff", width=2.5, capstyle=tk.ROUND
)
canvas.create_line(
    bottle_tip_x + nnx*0.8, bottle_tip_y + nny*0.8,
    neck_base_x + nnx*0.8, neck_base_y + nny*0.8,
    fill="#ffffff", width=1.5, capstyle=tk.ROUND
)

canvas.create_line(bottle_tip_x, bottle_tip_y, mx, my, fill="#f59e0b", width=4, capstyle=tk.ROUND)
canvas.create_line(bottle_tip_x, bottle_tip_y, mx, my, fill="#fef08a", width=2, capstyle=tk.ROUND)

for d in range(3):
    dx = mx + math.sin(phase * 4.0 + d) * 7.0
    dy = my + math.cos(phase * 4.0 + d) * 4.0
    canvas.create_oval(dx - 2, dy - 2, dx + 2, dy + 2, fill="#facc15", outline="#b45309", width=1)

# 4. ORBIT FRONT
for i in range(star_count):
    ang = phase * 1.8 + i * (2 * math.pi / star_count)
    sin_a = math.sin(ang)
    if sin_a >= 0:
        sx = head_x + math.cos(ang) * orbit_rx
        sy = head_y + sin_a * orbit_ry
        scale = 0.75 + 0.25 * (sin_a + 1.0) / 2.0
        font_sz = max(8, int(15 * scale))
        sym = "⭐" if i % 2 == 0 else "💫"
        canvas.create_text(sx, sy, text=sym, font=("Segoe UI Emoji", font_sz))

hic_y = head_y - 45 + math.sin(phase * 2.0) * 4
canvas.create_text(mx + 38, hic_y, text="*HIC !* 🍾🥴", font=("Impact", 12, "bold"), fill="#f59e0b")

root.update()
print("Drunk overlay rendered successfully!")
root.destroy()
