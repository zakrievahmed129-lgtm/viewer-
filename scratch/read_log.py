import json
log_path = r"C:\Users\zakri\.gemini\antigravity-ide\brain\e1523c36-0bb6-4c9d-acbc-701818457486\.system_generated\logs\transcript.jsonl"
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            obj = json.loads(line)
            step = obj.get("step_index")
            if step == 191:
                source = obj.get("source")
                content = obj.get("content")
                print(f"Step {step} [{source}]:\n{content}")
        except Exception:
            pass
