import subprocess
import json
import time

def submit_batch2_kai():
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

        # 1. Take snapshot of Tab 4 to get exact current UIDs of modal
        print("📸 Taking snapshot of modal...")
        send({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "take_snapshot", "arguments": {"pageId": 4}}
        })
        res2 = recv(2)
        snap = res2.get("result", {}).get("content", [{}])[0].get("text", "")
        
        textbox_uid = None
        checkbox_uid = None
        submit_btn_uid = None
        
        for line in snap.splitlines():
            if 'textbox "Clip link"' in line and "uid=" in line:
                for part in line.split():
                    if part.startswith("uid="):
                        textbox_uid = part.split("=")[1].strip('"')
            elif 'checkbox' in line and "uid=" in line:
                for part in line.split():
                    if part.startswith("uid="):
                        checkbox_uid = part.split("=")[1].strip('"')
            elif 'button "Submit clip"' in line and "uid=" in line:
                for part in line.split():
                    if part.startswith("uid="):
                        submit_btn_uid = part.split("=")[1].strip('"')

        print(f"Textbox UID: {textbox_uid}")
        print(f"Checkbox UID: {checkbox_uid}")
        print(f"Submit Button UID: {submit_btn_uid}")

        clip_url = "https://www.youtube.com/shorts/rMSxklEL-OM"
        print(f"⌨️ Pasting link: {clip_url} into {textbox_uid}...")
        send({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "fill", "arguments": {"pageId": 4, "uid": textbox_uid, "value": clip_url}}
        })
        recv(3)
        time.sleep(1)

        print(f"☑️ Clicking checkbox: {checkbox_uid}...")
        send({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "click", "arguments": {"pageId": 4, "uid": checkbox_uid}}
        })
        recv(4)
        time.sleep(1)

        # Snapshot to see if Submit button is enabled
        print("📸 Checking submit button state...")
        send({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "take_snapshot", "arguments": {"pageId": 4}}
        })
        res5 = recv(5)
        new_snap = res5.get("result", {}).get("content", [{}])[0].get("text", "")
        for line in new_snap.splitlines():
            if any(k in line.lower() for k in ["submit", "error", "linked", "minute"]):
                print("  ", line)

    finally:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    submit_batch2_kai()
