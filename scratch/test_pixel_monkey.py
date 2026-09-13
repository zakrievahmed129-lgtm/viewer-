# -*- coding: utf-8 -*-
"""
Test prototype — Singe Farceur Pixel Art
Sprite 32×32, rendu en grille 5×5 = 160×160 px visible
Animations frame-by-frame : idle, volume_change, laugh
"""
import tkinter as tk
import math
import time

# =============================================================================
# PALETTE DE COULEURS DU SINGE
# =============================================================================
_  = None           # Transparent (pas de pixel)
B  = "#1a1a2e"      # Noir profond (contour)
DB = "#3d2b1f"      # Brun très foncé (contour corps)
BR = "#8B4513"      # Brun chocolat (corps principal)
LB = "#A0522D"      # Brun clair (ventre intérieur)
BG = "#F5DEB3"      # Beige (ventre, museau)
SK = "#DEB887"      # Peau claire (visage intérieur)
WH = "#FFFFFF"      # Blanc (yeux)
BK = "#000000"      # Noir pur (pupilles)
RD = "#DC143C"      # Rouge (casquette)
DR = "#8B0000"      # Rouge foncé (ombre casquette)
TL = "#A0522D"      # Queue
DT = "#6B3410"      # Queue sombre
YL = "#FFD700"      # Jaune (notes de musique / étoiles)
OR = "#FF8C00"      # Orange (accent)
PK = "#FFB6C1"      # Rose (intérieur oreilles)
GR = "#2E8B57"      # Vert (yeux quand content)
NS = "#5C3317"      # Nez

# =============================================================================
# SPRITE FRAMES DU SINGE (32x32 grille)
# =============================================================================

def _make_monkey_idle_0():
    """Frame idle 0 — pose neutre, yeux ouverts"""
    g = [[_ for __ in range(32)] for ___ in range(32)]
    
    # === CASQUETTE (rangées 3-7) ===
    for x in range(11, 22):
        g[3][x] = DR
    for x in range(10, 23):
        g[4][x] = RD
    for x in range(10, 24):
        g[5][x] = RD
    for x in range(12, 21):
        g[6][x] = RD
    for x in range(13, 20):
        g[7][x] = DR
    
    # === TÊTE (rangées 8-16) ===
    for x in range(12, 21):
        g[8][x] = DB
    for x in range(11, 22):
        g[9][x] = BR
    for x in range(10, 23):
        g[10][x] = BR
    
    # Oreille gauche
    g[10][9] = DB; g[10][8] = BR
    g[11][8] = DB; g[11][7] = BR; g[11][9] = PK
    g[12][8] = DB; g[12][7] = BR; g[12][9] = PK
    g[13][8] = DB; g[13][9] = BR
    
    # Oreille droite
    g[10][23] = DB; g[10][24] = BR
    g[11][24] = DB; g[11][25] = BR; g[11][23] = PK
    g[12][24] = DB; g[12][25] = BR; g[12][23] = PK
    g[13][24] = DB; g[13][23] = BR
    
    # Face
    for x in range(10, 23):
        g[11][x] = BR
        g[12][x] = BR
        g[13][x] = BR
        g[14][x] = BR
        g[15][x] = BR
    
    # Museau beige
    for x in range(13, 20):
        g[12][x] = BG
        g[13][x] = BG
        g[14][x] = SK
    
    # Yeux
    g[11][12] = WH; g[11][13] = WH; g[11][14] = BK
    g[11][18] = BK; g[11][19] = WH; g[11][20] = WH
    g[12][12] = WH; g[12][13] = WH; g[12][14] = BK
    g[12][18] = BK; g[12][19] = WH; g[12][20] = WH
    
    # Nez
    g[13][15] = NS; g[13][16] = NS; g[13][17] = NS
    
    # Bouche (sourire)
    g[14][14] = DB; g[14][15] = BK; g[14][16] = BK; g[14][17] = BK; g[14][18] = DB
    
    # Contour bas tête
    for x in range(11, 22):
        g[16][x] = DB
    
    # === CORPS (rangées 17-24) ===
    for x in range(13, 20):
        g[17][x] = BR
    for y in range(18, 25):
        for x in range(11, 22):
            g[y][x] = BR
    for y in range(19, 24):
        for x in range(13, 20):
            g[y][x] = BG
    
    # Bras gauche
    for y in range(18, 23):
        g[y][10] = BR; g[y][9] = BR
    g[23][9] = SK; g[23][10] = SK
    g[22][9] = SK
    
    # Bras droit
    for y in range(18, 23):
        g[y][22] = BR; g[y][23] = BR
    g[23][22] = SK; g[23][23] = SK
    g[22][23] = SK
    
    # === JAMBES (rangées 25-29) ===
    for y in range(25, 29):
        g[y][12] = BR; g[y][13] = BR; g[y][14] = BR
    g[29][11] = DB; g[29][12] = DB; g[29][13] = DB; g[29][14] = DB; g[29][15] = DB
    
    for y in range(25, 29):
        g[y][18] = BR; g[y][19] = BR; g[y][20] = BR
    g[29][17] = DB; g[29][18] = DB; g[29][19] = DB; g[29][20] = DB; g[29][21] = DB
    
    # === QUEUE ===
    g[21][8] = TL; g[22][7] = TL; g[23][6] = TL; g[24][5] = TL
    g[25][4] = TL; g[25][3] = TL; g[26][3] = TL; g[27][4] = DT
    g[27][5] = DT; g[28][5] = DT; g[28][6] = DT
    
    return g


def _make_monkey_idle_1():
    """Frame idle 1 — yeux fermés (clignement)"""
    g = _make_monkey_idle_0()
    g[11][12] = BR; g[11][13] = BR; g[11][14] = BR
    g[11][18] = BR; g[11][19] = BR; g[11][20] = BR
    g[12][12] = DB; g[12][13] = DB; g[12][14] = DB
    g[12][18] = DB; g[12][19] = DB; g[12][20] = DB
    return g


def _make_monkey_volume_0():
    """Frame volume 0 — bras droit levé"""
    g = _make_monkey_idle_0()
    for y in range(18, 23):
        g[y][22] = _; g[y][23] = _
    g[17][22] = BR; g[17][23] = BR
    g[16][23] = BR; g[16][24] = BR
    g[15][24] = BR; g[15][25] = BR
    g[14][25] = SK; g[14][26] = SK
    g[15][26] = SK
    g[11][14] = WH; g[11][13] = BK
    g[11][18] = WH; g[11][19] = BK
    return g


def _make_monkey_volume_1():
    """Frame volume 1 — main tournée"""
    g = _make_monkey_volume_0()
    g[14][25] = _; g[14][26] = SK; g[14][27] = SK
    g[15][26] = _; g[15][27] = SK
    g[10][27] = YL; g[9][28] = YL; g[8][28] = YL; g[8][29] = YL
    g[11][28] = YL
    return g


def _make_monkey_laugh_0():
    """Frame rire 0 — bouche grande ouverte"""
    g = _make_monkey_idle_0()
    g[14][13] = DB; g[14][14] = BK; g[14][15] = RD; g[14][16] = RD
    g[14][17] = RD; g[14][18] = BK; g[14][19] = DB
    g[15][14] = DB; g[15][15] = BK; g[15][16] = BK; g[15][17] = BK; g[15][18] = DB
    g[11][12] = BR; g[11][13] = WH; g[11][14] = BR
    g[11][18] = BR; g[11][19] = WH; g[11][20] = BR
    g[12][12] = DB; g[12][13] = DB; g[12][14] = DB
    g[12][18] = DB; g[12][19] = DB; g[12][20] = DB
    return g


def _make_monkey_laugh_1():
    """Frame rire 1 — se tape le ventre"""
    g = _make_monkey_laugh_0()
    g[21][10] = _; g[21][9] = _; g[22][9] = _; g[22][10] = _
    g[20][11] = SK; g[20][12] = SK
    g[21][22] = _; g[21][23] = _; g[22][22] = _; g[22][23] = _
    g[20][20] = SK; g[20][21] = SK
    return g


MONKEY_IDLE_FRAMES = [_make_monkey_idle_0, _make_monkey_idle_1, _make_monkey_idle_0, _make_monkey_idle_0]
MONKEY_VOLUME_FRAMES = [_make_monkey_volume_0, _make_monkey_volume_1, _make_monkey_volume_0, _make_monkey_volume_1]
MONKEY_LAUGH_FRAMES = [_make_monkey_laugh_0, _make_monkey_laugh_1, _make_monkey_laugh_0, _make_monkey_laugh_1]


class PixelArtRenderer:
    def __init__(self, canvas, offset_x=0, offset_y=0, cell_size=5):
        self.canvas = canvas
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.cell_size = cell_size
        self.pixel_ids = {}
    
    def render_frame(self, grid):
        cs = self.cell_size
        ox, oy = self.offset_x, self.offset_y
        for gy in range(len(grid)):
            row = grid[gy]
            for gx in range(len(row)):
                color = row[gx]
                key = (gx, gy)
                if key in self.pixel_ids:
                    item_id = self.pixel_ids[key]
                    if color is None:
                        self.canvas.itemconfig(item_id, fill="", outline="", state="hidden")
                    else:
                        self.canvas.itemconfig(item_id, fill=color, outline="", state="normal")
                else:
                    x1 = ox + gx * cs
                    y1 = oy + gy * cs
                    x2 = x1 + cs
                    y2 = y1 + cs
                    if color is not None:
                        item_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="", width=0)
                    else:
                        item_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="", outline="", width=0, state="hidden")
                    self.pixel_ids[key] = item_id
    
    def clear(self):
        for item_id in self.pixel_ids.values():
            self.canvas.delete(item_id)
        self.pixel_ids.clear()


class TestMonkeyWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Singe Farceur - Pixel Art")
        self.root.configure(bg="#1a1a2e")
        self.root.geometry("600x500")
        
        tk.Label(self.root, text="SINGE FARCEUR - Pixel Art Preview",
                 font=("Consolas", 14, "bold"), fg="#FFD700", bg="#1a1a2e").pack(pady=10)
        
        self.canvas = tk.Canvas(self.root, width=500, height=350, bg="#0d0d1a",
                                highlightthickness=1, highlightbackground="#333")
        self.canvas.pack(pady=10)
        
        ctrl = tk.Frame(self.root, bg="#1a1a2e")
        ctrl.pack(pady=5)
        
        tk.Button(ctrl, text="Idle", command=lambda: self.set_anim("idle"),
                  bg="#2d2d44", fg="white", font=("Consolas", 10)).pack(side="left", padx=5)
        tk.Button(ctrl, text="Volume", command=lambda: self.set_anim("volume"),
                  bg="#2d2d44", fg="white", font=("Consolas", 10)).pack(side="left", padx=5)
        tk.Button(ctrl, text="Laugh", command=lambda: self.set_anim("laugh"),
                  bg="#2d2d44", fg="white", font=("Consolas", 10)).pack(side="left", padx=5)
        
        self.info_label = tk.Label(self.root, text="Animation: idle | Frame: 0",
                                   font=("Consolas", 9), fg="#888", bg="#1a1a2e")
        self.info_label.pack()
        
        self.renderer = PixelArtRenderer(self.canvas, offset_x=170, offset_y=20, cell_size=5)
        self.current_anim = "idle"
        self.frame_idx = 0
        self.tick_count = 0
        
        self.frames = {
            "idle": [f() for f in MONKEY_IDLE_FRAMES],
            "volume": [f() for f in MONKEY_VOLUME_FRAMES],
            "laugh": [f() for f in MONKEY_LAUGH_FRAMES]
        }
        
        self._tick()
        self.root.mainloop()
    
    def set_anim(self, name):
        self.current_anim = name
        self.frame_idx = 0
    
    def _tick(self):
        self.tick_count += 1
        if self.tick_count % 8 == 0:
            frames = self.frames[self.current_anim]
            self.frame_idx = (self.frame_idx + 1) % len(frames)
        
        frames = self.frames[self.current_anim]
        grid = frames[self.frame_idx]
        self.renderer.render_frame(grid)
        
        self.info_label.config(text=f"Animation: {self.current_anim} | Frame: {self.frame_idx}/{len(frames)-1}")
        self.root.after(16, self._tick)


if __name__ == "__main__":
    TestMonkeyWindow()
