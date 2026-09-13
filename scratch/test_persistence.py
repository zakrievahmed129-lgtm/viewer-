import os
import sys
import json
import winreg

def get_state_file_path():
    return os.path.join(os.environ.get('LOCALAPPDATA', os.environ.get('TEMP', '')), 'ghost_state.json')

def save_state(phase):
    try:
        state_file = get_state_file_path()
        state_data = {
            "phase": phase,
            "mouse_fight_count": 10,
            "notepad_close_count": 2,
            "cmd_close_count": 1,
            "alt_tab_attempt_count": 0,
            "escape_attempt_count": 4,
            "alt_f4_attempt_count": 3,
            "win_key_attempt_count": 0,
            "task_manager_attempt_count": 0,
            "focus_loss_attempt_count": 0,
            "shutdown_count": 0
        }
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=4)
        print("[*] State saved successfully.")
    except Exception as e:
        print(f"[!] Error saving state: {e}")

def load_state():
    try:
        state_file = get_state_file_path()
        if os.path.exists(state_file):
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data["shutdown_count"] = data.get("shutdown_count", 0) + 1
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return data
    except Exception as e:
        print(f"[!] Error loading state: {e}")
    return None

def clear_state():
    try:
        state_file = get_state_file_path()
        if os.path.exists(state_file):
            os.remove(state_file)
            print("[*] State cleared successfully.")
    except Exception as e:
        print(f"[!] Error clearing state: {e}")

def add_to_startup():
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        cmd_line = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "GhostProtocolTest", 0, winreg.REG_SZ, cmd_line)
        winreg.CloseKey(key)
        print("[*] Added to startup registry.")
    except Exception as e:
        print(f"[!] Error adding to startup: {e}")

def remove_from_startup():
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "GhostProtocolTest")
        winreg.CloseKey(key)
        print("[*] Removed from startup registry.")
    except Exception as e:
        print(f"[!] Error removing from startup: {e}")

if __name__ == "__main__":
    print("Testing GHOST state persistence...")
    save_state(5)
    
    state = load_state()
    if state:
        print(f"Loaded state: {state}")
    
    add_to_startup()
    remove_from_startup()
    clear_state()
