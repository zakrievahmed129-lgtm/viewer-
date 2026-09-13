with open("ghost_script.py", "r", encoding="utf-8") as f:
    text = f.read()

pos1 = text.find("class CartoonPullerOverlay:")
pos2 = text.find("def ensure_prank_overlays_started():")
pos3 = text.find("def _ghost_sounds_loop():")
pos4 = text.find("def toggle_ghost_sounds(active):")
pos5 = text.find("class ElusiveWindowLegsOverlay:")
pos6 = text.find("def ensure_legs_overlay_started():")

print(f"Cartoon overlays block: {pos1} to {pos2}")
print(f"Ghost sounds loop block: {pos3} to {pos4}")
print(f"Elusive legs overlay block: {pos5} to {pos6}")

assert pos1 != -1 and pos2 != -1 and pos3 != -1 and pos4 != -1 and pos5 != -1 and pos6 != -1
print("All anchor points verified successfully!")
