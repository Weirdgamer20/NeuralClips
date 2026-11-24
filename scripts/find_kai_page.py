import subprocess
import json

def find_kai_page():
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

    # Try evaluating window.location.href on each pageId 1, 2, 3, 4
    for pid in [1, 2, 3, 4]:
        send({
            "jsonrpc": "2.0",
            "id": 10 + pid,
            "method": "tools/call",
            "params": {
                "name": "evaluate_script",
                "arguments": {
                    "pageId": pid,
                    "expression": "JSON.stringify({href: window.location.href, title: document.title})"
                }
            }
        })

    # Read responses
    for _ in range(10):
        line = p.stdout.readline()
        if line:
            try:
                msg = json.loads(line)
                if msg.get("id") in [11, 12, 13, 14]:
                    print(f"PageId {msg['id'] - 10}:", msg.get("result", {}).get("content"))
            except Exception:
                pass

    p.terminate()

if __name__ == "__main__":
    find_kai_page()
