import subprocess
import json

def get_full_snapshot():
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

    send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    send({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "take_snapshot",
            "arguments": {"pageId": 3}
        }
    })

    while True:
        line = p.stdout.readline()
        if not line:
            break
        msg = json.loads(line)
        if msg.get("id") == 2:
            content = msg.get("result", {}).get("content", [])
            for c in content:
                text = c.get("text", "")
                with open(str(BASE_DIR / "storage" / "page3_snapshot.txt"), "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Wrote {len(text)} characters to storage/page3_snapshot.txt")
            break

    p.terminate()

if __name__ == "__main__":
    get_full_snapshot()
