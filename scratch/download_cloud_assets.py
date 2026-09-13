import os
import urllib.request

out_dir = r"assets/monkey"
os.makedirs(out_dir, exist_ok=True)

urls = [
    ("monkey_anim_prev.gif", "https://da8ztllw6by0f.cloudfront.net/4c6164a29f8676b500213822631f980f.gif"),
    ("monkey_spritesheet_prev.png", "https://da8ztllw6by0f.cloudfront.net/2b7feb32a3458bf7a2721757de376013.png"),
    ("monkey_volume_anim.gif", "https://da8ztllw6by0f.cloudfront.net/e2590cd3c7b32b651e8bd0001f398c0c.gif"),
    ("monkey_volume_spritesheet.png", "https://da8ztllw6by0f.cloudfront.net/53e23f016d2bd7e7b5df11ffe919fb20.png"),
]

for name, url in urls:
    path = os.path.join(out_dir, name)
    print(f"Downloading {url} to {path}...")
    try:
        urllib.request.urlretrieve(url, path)
        print(f"  Success: {os.path.getsize(path)} bytes")
    except Exception as e:
        print(f"  Failed: {e}")
