import subprocess
import json
import time

def list_open_pages():
    p = subprocess.Popen(
        ["npx.cmd", "-y", "chrome-devtools-mcp@latest", "--autoConnect"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )

    def send_rpc(msg):
        p.stdin.write(json.dumps(msg) + "\n")
        p.stdin.flush()

    send_rpc({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    })

    line1 = p.stdout.readline()
    print("Init response:", line1[:200])

    send_rpc({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "notifications/initialized"
    })

    send_rpc({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "list_pages",
            "arguments": {}
        }
    })

    for _ in range(5):
        line = p.stdout.readline()
        if line:
            print("Response:", line[:300])

    p.terminate()

if __name__ == "__main__":
    list_open_pages()
