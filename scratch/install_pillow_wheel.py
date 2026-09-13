import urllib.request
import json
import zipfile
import io
import os
import sys
import shutil

def main():
    try:
        import ssl
        ssl_context = ssl._create_unverified_context()
        # 1. Fetch PyPI metadata
        print("Fetching Pillow release metadata from PyPI...")
        url = "https://pypi.org/pypi/pillow/json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ssl_context) as response:
            data = json.loads(response.read().decode())

        # 2. Find cp312 win_amd64 wheel in the latest version or previous ones
        latest_version = data["info"]["version"]
        print(f"Latest Pillow version: {latest_version}")
        
        wheel_url = None
        # First search latest version
        for r in data["releases"].get(latest_version, []):
            filename = r["filename"]
            if "cp312" in filename and "win_amd64" in filename and filename.endswith(".whl"):
                wheel_url = r["url"]
                break
                
        # If not found, search all releases
        if not wheel_url:
            print("Searching in other release versions...")
            for ver, rels in data["releases"].items():
                for r in rels:
                    filename = r["filename"]
                    if "cp312" in filename and "win_amd64" in filename and filename.endswith(".whl"):
                        wheel_url = r["url"]
                        print(f"Found compatible wheel in version {ver}")
                        break
                if wheel_url:
                    break

        if not wheel_url:
            print("Error: No compatible Pillow wheel found on PyPI for Python 3.12 win_amd64.")
            sys.exit(1)

        print(f"Downloading wheel: {wheel_url.split('/')[-1]}")
        with urllib.request.urlopen(wheel_url, context=ssl_context) as resp:
            wheel_bytes = resp.read()

        # 3. Extract to site-packages
        # We target the virtualenv's site-packages
        # The virtualenv python is running this script, so sys.path has it.
        site_packages = None
        for p in sys.path:
            if "site-packages" in p and "venv" in p:
                site_packages = p
                break
                
        if not site_packages:
            # Fallback path construct
            site_packages = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venv", "lib", "python3.12", "site-packages")
            
        print(f"Extracting to site-packages directory: {site_packages}")
        if not os.path.exists(site_packages):
            os.makedirs(site_packages)
            
        with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as z:
            z.extractall(site_packages)

        print("Pillow extracted. Renaming/copying .pyd files for MinGW compatibility...")
        pil_dir = os.path.join(site_packages, "PIL")
        for filename in os.listdir(pil_dir):
            if filename.endswith("win_amd64.pyd"):
                base_name = filename.split(".")[0] # e.g. _imaging
                src_path = os.path.join(pil_dir, filename)
                
                # Copy to plain .pyd
                dst_plain = os.path.join(pil_dir, f"{base_name}.pyd")
                shutil.copy2(src_path, dst_plain)
                
                # Copy to MinGW tag
                dst_mingw = os.path.join(pil_dir, f"{base_name}.cp312-mingw_x86_64_ucrt_gnu.pyd")
                shutil.copy2(src_path, dst_mingw)
                print(f"Copied {filename} to {base_name}.pyd and MinGW tag.")

        print("Pillow has been successfully installed and extracted!")
        
        # Test import
        from PIL import ImageGrab
        print("Import test passed! ImageGrab is importable.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
