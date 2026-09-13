# -*- coding: utf-8 -*-
"""
Test de simulation de la physique de glisse sur glace pour la fenêtre fuyante.
"""
import math
import time

def simulate_evasion(curr_x, curr_y, w_width, w_height, mx, my, sw=1920, sh=1080):
    min_x, max_x = 10, sw - w_width - 10
    min_y, max_y = 10, sh - w_height - 10
    
    cx = curr_x + w_width / 2.0
    cy = curr_y + w_height / 2.0
    
    # Distance souris - boîte
    closest_x = max(curr_x, min(curr_x + w_width, mx))
    closest_y = max(curr_y, min(curr_y + w_height, my))
    dist_to_edge = math.hypot(closest_x - mx, closest_y - my)
    
    danger_radius = 240.0
    if dist_to_edge > danger_radius:
        return 0, 0, "Calme"
        
    urgency = max(0.0, min(1.0, (danger_radius - dist_to_edge) / danger_radius))
    
    # Vecteur souris -> centre fenêtre
    vx = cx - mx
    vy = cy - my
    dist = math.hypot(vx, vy)
    if dist == 0:
        vx, vy, dist = 1.0, 0.0, 1.0
    norm_x = vx / dist
    norm_y = vy / dist
    
    # Détection des murs et coins
    near_left = (curr_x - min_x) < 140
    near_right = (max_x - curr_x) < 140
    near_top = (curr_y - min_y) < 140
    near_bottom = (max_y - curr_y) < 140
    
    is_corner = (near_left or near_right) and (near_top or near_bottom)
    is_wall = near_left or near_right or near_top or near_bottom
    
    base_accel = 12.0 + 38.0 * (urgency ** 1.3)
    push_x = norm_x * base_accel
    push_y = norm_y * base_accel
    
    action = "Fuite normale"
    
    if is_corner:
        action = "Esquive d'urgence Coin (Juke)"
        # La fenêtre est acculée dans un coin
        # Elle doit glisser rapidement le long de l'axe le plus dégagé ou vers l'intérieur
        to_center_x = (sw / 2.0) - cx
        to_center_y = (sh / 2.0) - cy
        c_dist = math.hypot(to_center_x, to_center_y) or 1.0
        
        # Choix de la trajectoire de fuite en arc
        corner_boost = 35.0 * (0.5 + urgency)
        push_x += (to_center_x / c_dist) * corner_boost
        push_y += (to_center_y / c_dist) * corner_boost
        
    elif is_wall:
        action = "Glisse le long du mur"
        wall_slide_boost = 24.0 * (0.4 + urgency)
        if near_left or near_right:
            # Glisse vers le haut ou le bas selon la position de la souris
            slide_dir = 1.0 if my <= cy else -1.0
            push_y += slide_dir * wall_slide_boost
            # Léger rebond vers l'intérieur
            push_x += (15.0 if near_left else -15.0) * urgency
        elif near_top or near_bottom:
            slide_dir = 1.0 if mx <= cx else -1.0
            push_x += slide_dir * wall_slide_boost
            push_y += (15.0 if near_top else -15.0) * urgency
            
    return push_x, push_y, action

if __name__ == "__main__":
    # Test 1: Fenêtre coincée dans le coin haut-gauche (x=10, y=10)
    # Souris arrive de bas-droite (x=120, y=120)
    px, py, act = simulate_evasion(10, 10, 300, 200, 120, 120)
    print(f"Test Coin Haut-Gauche: Action={act}, PushX={px:.1f}, PushY={py:.1f}")
    assert px > 0 or py > 0, "La fenêtre doit fuir le coin vers l'intérieur!"

    # Test 2: Fenêtre contre le mur gauche (x=10, y=500), souris arrive de droite (x=150, y=500)
    px, py, act = simulate_evasion(10, 500, 300, 200, 150, 500)
    print(f"Test Mur Gauche: Action={act}, PushX={px:.1f}, PushY={py:.1f}")
    assert abs(py) > 10, "La fenêtre doit glisser le long du mur!"

    print("Tests physiques validés avec succès!")
