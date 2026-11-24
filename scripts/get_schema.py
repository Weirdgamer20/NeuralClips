import subprocess
import json

def get_tool_schema():
    p = subprocess.Popen(
        ["npx.cmd", "-y", "chrome-devtools-mcp@latest", "--autoConnect"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,
        bufsize=1
    )

    def send(obj):
        p.stdin.write(json.dumps(obj) + "\n")
        p.stdin.flush()

    send({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "agent", "version": "1.0"}
        }
    })

    while True:
        line = p.stdout.readline()
        if not line or json.loads(line).get("id") == 1:
            break

    send({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    })

    while True:
        line = p.stdout.readline()
        if not line:
            break
        msg = json.loads(line)
        if msg.get("id") == 2:
            tools = msg.get("result", {}).get("tools", [])
            for t in tools:
                if t["name"] == "evaluate_script":
                    print("evaluate_script schema:", json.dumps(t["inputSchema"], indent=2))
            break

    p.terminate()

if __name__ == "__main__":
    get_tool_schema()
