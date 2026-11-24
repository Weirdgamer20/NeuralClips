import subprocess
import json

def inspect_page_3():
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

    # 1. Initialize
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

    # 2. Take snapshot of page 3
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
            print("SNAPSHOT FOR PAGE 3:")
            res = msg.get("result", {})
            content = res.get("content", [])
            for c in content:
                print(c.get("text", "")[:2000])
            break

    p.terminate()

if __name__ == "__main__":
    inspect_page_3()
