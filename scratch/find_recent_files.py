import os, time

now = time.time()
recent_files = []

search_dirs = [
    os.path.expanduser(r"~\AppData\Local\Google"),
    os.path.expanduser(r"~\AppData\Local\Temp"),
    os.path.expanduser(r"~\Downloads"),
]

for d in search_dirs:
    if not os.path.exists(d):
        continue
    for root, dirs, files in os.walk(d):
        for f in files:
            if any(f.lower().endswith(ext) for ext in ['.png', '.gif', '.webp', '.zip']):
                fp = os.path.join(root, f)
                try:
                    mtime = os.path.getmtime(fp)
                    if now - mtime < 1200: # last 20 mins
                        recent_files.append((mtime, fp, os.path.getsize(fp)))
                except:
                    pass

recent_files.sort(reverse=True)
for mt, fp, sz in recent_files[:20]:
    print(f"{time.strftime('%H:%M:%S', time.localtime(mt))} ({sz} B): {fp}")
