import tkinter as tk
import ctypes
import math
import random
import time

# Mock states
puller_state = {"active": True, "mx": 400, "my": 300, "dir_x": 1.0, "dir_y": 0.0, "force": 1.0}
drunk_state = {"active": True, "mx": 400, "my": 300, "intro_reset": False}
wall_state = {"active": True, "mx": 400, "my": 300, "is_bonking": True, "wall_x": 380}
painter_state = {"active": True}
keys_state = {"active": True, "last_key_time": time.time(), "key_char": "A"}
ghost_state = {"active": True, "booh": True}
tts_state = {"active": True, "is_speaking": True, "text": "ALERTE SYSTÈME !"}
rotate_state = {"active": True, "angle": 45.0}
legs_state = {"active": True, "target_cx": 400, "target_bottom": 300, "is_moving": True, "dir_x": 1.0, "speed": 22.0}

print("Mock states defined successfully")
