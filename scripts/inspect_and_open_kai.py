import subprocess
import json
import time

def open_kai_campaign():
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

    def recv(req_id):
        while True:
            line = p.stdout.readline()
            if not line:
                return None
            try:
                msg = json.loads(line)
                if msg.get("id") == req_id:
                    return msg
            except Exception:
                continue

    try:
        # 1. Init
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
        recv(1)
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})

        # 2. Take Snapshot of Tab 4
        print("📸 Taking snapshot of Tab 4...")
        send({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "take_snapshot", "arguments": {"pageId": 4}}
        })
        res2 = recv(2)
        snap_text = res2.get("result", {}).get("content", [{}])[0].get("text", "")
        
        kai_uid = None
        for line in snap_text.splitlines():
            if "Kai Cenat" in line and "uid=" in line:
                print("Found Kai line:", line)
                # Extract uid
                for part in line.split():
                    if part.startswith("uid="):
                        kai_uid = part.split("=")[1].strip('"')
                        break
        
        print(f"👉 Kai Cenat button UID: {kai_uid}")
        if not kai_uid:
            print("Could not find Kai Cenat button UID!")
            return

        # 3. Click the Kai Cenat button
        print(f"🖱️ Clicking Kai Cenat ({kai_uid})...")
        send({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "click", "arguments": {"pageId": 4, "uid": kai_uid}}
        })
        res3 = recv(3)
        print("Click response:", res3)
        time.sleep(2)

        # 4. Take Snapshot after click
        print("📸 Taking snapshot after opening campaign...")
        send({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "take_snapshot", "arguments": {"pageId": 4}}
        })
        res4 = recv(4)
        new_snap = res4.get("result", {}).get("content", [{}])[0].get("text", "")
        with open("d:/vidclip/storage/kai_campaign_opened.txt", "w", encoding="utf-8") as f:
            f.write(new_snap)
        print(f"Saved new snapshot ({len(new_snap)} bytes) to storage/kai_campaign_opened.txt")

    finally:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    open_kai_campaign()
