import json

with open(r'C:\Users\zakri\.gemini\antigravity-ide\brain\785ab520-7bc2-4e75-84d4-2c1cc59a0a49\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        step_idx = data.get('step_index', 0)
        # Check subagent calls or responses that contain DOM
        content = str(data.get('content', ''))
        if 'spritesheet' in content.lower() or 'gallery' in content.lower():
            # check if there's DOM snippet
            if '<img' in content or 'src=' in content or 'Image' in content:
                print(f"Step {step_idx} length: {len(content)}")
                for line_c in content.split('\n'):
                    if any(k in line_c.lower() for k in ['src', 'img', 'url', 'button', 'download', 'blob']):
                        print("  LINE:", line_c[:150])
