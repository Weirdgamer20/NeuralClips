import subprocess
import json
import time

def main():
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
        data = json.dumps(obj)
        p.stdin.write(data + "\n")
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

    # Read init
    while True:
        line = p.stdout.readline()
        if not line:
            break
        msg = json.loads(line)
        if msg.get("id") == 1:
            break

    # 2. Initialized notification
    send({
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    })

    # 3. Call list_pages
    send({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "list_pages",
            "arguments": {}
        }
    })

    # Read list_pages response
    while True:
        line = p.stdout.readline()
        if not line:
            break
        msg = json.loads(line)
        if msg.get("id") == 2:
            print("PAGES RESPONSE:")
            print(json.dumps(msg, indent=2))
            break

    p.terminate()

if __name__ == "__main__":
    main()
