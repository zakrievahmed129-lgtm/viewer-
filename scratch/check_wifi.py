import subprocess
import re

def get_wifi_profiles():
    try:
        # Get profiles list
        meta_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], stderr=subprocess.STDOUT, shell=True).decode('utf-8', errors='ignore')
        profiles = re.findall(r":\s(.*)", meta_data)
        # Clean profiles
        profiles = [p.strip() for p in profiles if p.strip()]
        
        wifi_list = []
        for profile in profiles[:6]: # limit to 6 profiles
            try:
                # Get security type and password
                detail_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', f'name={profile}', 'key=clear'], stderr=subprocess.STDOUT, shell=True).decode('utf-8', errors='ignore')
                
                # Find security type
                security = "WPA2"
                sec_match = re.search(r"Authentification\s*:\s*(.*)|Authentication\s*:\s*(.*)", detail_data)
                if sec_match:
                    sec_val = sec_match.group(1) or sec_match.group(2)
                    if sec_val:
                        security = sec_val.strip()
                
                # Find password
                password = ""
                pass_match = re.search(r"Contenu de la cl\s*:\s*(.*)|Key Content\s*:\s*(.*)", detail_data)
                if pass_match:
                    pass_val = pass_match.group(1) or pass_match.group(2)
                    if pass_val:
                        password = pass_val.strip()
                
                if not password:
                    password = "[Non crypté / Non trouvé]"
                
                wifi_list.append((profile, security, password))
            except Exception as e:
                wifi_list.append((profile, "Inconnu", "[Erreur d'accès]"))
        return wifi_list
    except Exception as e:
        print("Error getting wifi profiles:", e)
        return []

if __name__ == "__main__":
    profiles = get_wifi_profiles()
    for ssid, sec, pwd in profiles:
        print(f"SSID: {ssid} | Sec: {sec} | Password: {pwd}")
