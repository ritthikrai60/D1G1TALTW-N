import json

with open(r'C:\Users\ritth\.gemini\antigravity\brain\6c13c66f-33c4-4cae-a03d-a050b2641bb8\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        d = json.loads(line)
        t = d.get('type')
        src = d.get('source')
        idx = d.get('step_index')
        if src == 'USER_EXPLICIT' or t == 'USER_INPUT':
            print(f'=== STEP {idx} USER ===: {d.get("content")}')
        elif t == 'PLANNER_RESPONSE' and not d.get('tool_calls'):
            c = str(d.get('content'))
            print(f'=== STEP {idx} ASST ===: {c[:250]}...')

