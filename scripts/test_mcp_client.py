import subprocess
import json
import time

def query_mcp():
    p = subprocess.Popen(
        ["npx.cmd", "-y", "chrome-devtools-mcp@latest", "--autoConnect"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )

    def send_rpc(msg):
        body = json.dumps(msg) + "\n"
        p.stdin.write(body)
        p.stdin.flush()

    # Step 1: Initialize
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

    time.sleep(2)

    # Step 2: List tools
    send_rpc({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    })

    time.sleep(2)

    # Read responses
    p.terminate()
    stdout, stderr = p.communicate()
    print("--- STDOUT RESPONSES ---")
    for line in stdout.splitlines():
        if line.strip():
            try:
                data = json.loads(line)
                if data.get("id") == 2:
                    tools = [t["name"] for t in data.get("result", {}).get("tools", [])]
                    print(f"Available MCP Tools ({len(tools)}):", tools)
                else:
                    print(data)
            except Exception:
                print(line[:200])

if __name__ == "__main__":
    query_mcp()
