import json
import subprocess
from pathlib import Path

target_dir = Path(r"C:\Users\ritth\.gemini\antigravity\mcp\ingetrazo")
target_dir.mkdir(parents=True, exist_ok=True)

proc = subprocess.Popen(
    [r"C:\Program Files\IngeTrazo\ingetrazo-mcp.exe"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
    encoding="utf-8"
)

reqs = (
    json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "antigravity", "version": "1.0"}
        }
    }) + "\n" +
    json.dumps({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }) + "\n"
)

stdout, _ = proc.communicate(reqs)

lines = [l.strip() for l in stdout.strip().split("\n") if l.strip()]
resp1 = json.loads(lines[0])
resp2 = json.loads(lines[1])

instructions = resp1.get("result", {}).get("instructions", "")
(target_dir / "instructions.md").write_text("# IngeTrazo MCP Server Instructions\n\n" + instructions, encoding="utf-8")

tools = resp2.get("result", {}).get("tools", [])
for t in tools:
    schema = {
        "name": t["name"],
        "description": t.get("description", ""),
        "parameters": t.get("inputSchema", {})
    }
    tool_file = target_dir / f"{t['name']}.json"
    tool_file.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")

print("Generated tools:", [t["name"] for t in tools])

