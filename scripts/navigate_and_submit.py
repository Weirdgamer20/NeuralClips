import subprocess
import json
import time

def submit_clip(campaign_url: str, clip_url: str, tab_id: int = 1):
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
        # 1. Init Handshake
        send({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "antigravity-ai", "version": "1.0"}
            }
        })
        recv(1)
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})

        # 2. Navigate to Campaign URL
        print(f"🚀 Navigating Tab [{tab_id}] to campaign: {campaign_url} ...")
        send({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "navigate_page",
                "arguments": {"pageId": tab_id, "url": campaign_url}
            }
        })
        res2 = recv(2)
        print("Navigation done. Waiting for DOM to settle...")
        time.sleep(4)

        # 3. Snapshot to find "Submit clip" button
        print("📸 Taking snapshot of campaign page...")
        send({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "take_snapshot", "arguments": {"pageId": tab_id}}
        })
        res3 = recv(3)
        snap1 = res3.get("result", {}).get("content", [{}])[0].get("text", "")
        
        submit_btn_uid = None
        for line in snap1.splitlines():
            if 'button "Submit clip"' in line and "uid=" in line:
                for part in line.split():
                    if part.startswith("uid="):
                        submit_btn_uid = part.split("=")[1].strip('"')
                        break
        
        print(f"👉 Submit Button UID: {submit_btn_uid}")
        if not submit_btn_uid:
            print("Could not find 'Submit clip' button on page. Here are buttons found:")
            for l in snap1.splitlines():
                if "button" in l:
                    print("  ", l)
            return False

        # 4. Click "Submit clip"
        print(f"🖱️ Clicking 'Submit clip' ({submit_btn_uid})...")
        send({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "click", "arguments": {"pageId": tab_id, "uid": submit_btn_uid}}
        })
        recv(4)
        time.sleep(2)

        # 5. Snapshot modal
        print("📸 Taking snapshot of submission dialog...")
        send({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "take_snapshot", "arguments": {"pageId": tab_id}}
        })
        res5 = recv(5)
        snap2 = res5.get("result", {}).get("content", [{}])[0].get("text", "")

        textbox_uid = None
        checkbox_uid = None
        dialog_submit_uid = None

        for line in snap2.splitlines():
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
                        dialog_submit_uid = part.split("=")[1].strip('"')

        print(f"Textbox UID: {textbox_uid}")
        print(f"Checkbox UID: {checkbox_uid}")
        print(f"Final Submit UID: {dialog_submit_uid}")

        if not textbox_uid or not checkbox_uid or not dialog_submit_uid:
            print("Could not locate all modal controls. Dialog snapshot:")
            for l in snap2.splitlines()[:30]:
                print("  ", l)
            return False

        # 6. Fill clip link
        print(f"⌨️ Pasting clip URL: {clip_url} ...")
        send({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {"name": "fill", "arguments": {"pageId": tab_id, "uid": textbox_uid, "value": clip_url}}
        })
        recv(6)
        time.sleep(1)

        # 7. Check the compliance checkbox
        print(f"☑️ Clicking compliance checkbox ({checkbox_uid})...")
        send({
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {"name": "click", "arguments": {"pageId": tab_id, "uid": checkbox_uid}}
        })
        recv(7)
        time.sleep(1)

        # 8. Click Submit
        print(f"🚀 Clicking Final 'Submit clip' button ({dialog_submit_uid})...")
        send({
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {"name": "click", "arguments": {"pageId": tab_id, "uid": dialog_submit_uid}}
        })
        res8 = recv(8)
        print("Submit response:", res8)
        time.sleep(3)

        # 9. Verify outcome
        send({
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {"name": "take_snapshot", "arguments": {"pageId": tab_id}}
        })
        res9 = recv(9)
        snap3 = res9.get("result", {}).get("content", [{}])[0].get("text", "")
        print("\n--- OUTCOME VERIFICATION ---")
        for line in snap3.splitlines()[:25]:
            if any(k in line.lower() for k in ["submitted", "success", "error", "approved", "dialog", "clip"]):
                print("  ", line)

        return True

    finally:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    kai_campaign = "https://contentrewards.com/c/campaigns/1d2bcb00-c904-415f-aa82-f95b96baad86"
    sample_clip = "https://www.youtube.com/shorts/q4NlSmY94w8"
    submit_clip(kai_campaign, sample_clip, tab_id=1)
