import subprocess
import json
import time

def click_submit_clip():
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
        # Init
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

        # 1. Take snapshot of Tab 4 to find Submit clip button
        print("📸 Taking snapshot of Tab 4...")
        send({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "take_snapshot", "arguments": {"pageId": 4}}
        })
        res2 = recv(2)
        snap_text = res2.get("result", {}).get("content", [{}])[0].get("text", "")
        
        submit_uid = None
        for line in snap_text.splitlines():
            if "Submit clip" in line and "uid=" in line:
                print("Found Submit button line:", line)
                for part in line.split():
                    if part.startswith("uid="):
                        submit_uid = part.split("=")[1].strip('"')
                        break
        
        print(f"👉 Submit button UID: {submit_uid}")
        if not submit_uid:
            return

        # 2. Click Submit clip button
        print(f"🖱️ Clicking 'Submit clip' ({submit_uid})...")
        send({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "click", "arguments": {"pageId": 4, "uid": submit_uid}}
        })
        recv(3)
        time.sleep(2)

        # 3. Take snapshot of submission modal
        print("📸 Snapshot after clicking Submit clip...")
        send({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "take_snapshot", "arguments": {"pageId": 4}}
        })
        res4 = recv(4)
        modal_snap = res4.get("result", {}).get("content", [{}])[0].get("text", "")
        with open(str(BASE_DIR / "storage" / "submit_modal_snapshot.txt"), "w", encoding="utf-8") as f:
            f.write(modal_snap)
        print("Modal snapshot written to storage/submit_modal_snapshot.txt")

    finally:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    click_submit_clip()
