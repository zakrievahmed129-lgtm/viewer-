import re

with open(r'C:\Users\zakri\.gemini\antigravity-ide\brain\785ab520-7bc2-4e75-84d4-2c1cc59a0a49\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    text = f.read()

urls = set(re.findall(r'https?://[^\s\"\'<>]+', text))
for u in sorted(urls):
    if any(ext in u.lower() for ext in ['.png', '.gif', '.webp', '.jpg', 'api', 'storage', 'cdn', 'retro', 'generated']):
        print(u)
