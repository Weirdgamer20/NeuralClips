import subprocess
import json
import time

def run_submission_on_tab3(campaign_url, clip_url):
    print("=" * 60)
    print(f"🚀 Submitting to: {campaign_url}")
    print(f"🎬 Clip: {clip_url}")
    print("=" * 60)

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
        # Handshake
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

        # Navigate Tab 3 to campaign
        send({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "navigate_page",
                "arguments": {"pageId": 3, "url": campaign_url}
            }
        })
        recv(2)
        time.sleep(3)

        # Snapshot Tab 3
        send({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "take_snapshot", "arguments": {"pageId": 3}}
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
        
        print(f"Submit clip button: {submit_btn_uid}")
        if not submit_btn_uid:
            print("Submit clip button not found on campaign page!")
            return False

        # Click Submit clip
        send({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "click", "arguments": {"pageId": 3, "uid": submit_btn_uid}}
        })
        recv(4)
        time.sleep(2)

        # Snapshot modal
        send({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "take_snapshot", "arguments": {"pageId": 3}}
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

        print(f"Textbox: {textbox_uid} | Checkbox: {checkbox_uid} | Dialog Submit: {dialog_submit_uid}")
        if not textbox_uid or not checkbox_uid or not dialog_submit_uid:
            print("Modal inputs not found!")
            return False

        # Fill URL
        send({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {"name": "fill", "arguments": {"pageId": 3, "uid": textbox_uid, "value": clip_url}}
        })
        recv(6)
        time.sleep(1)

        # Click Checkbox
        send({
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {"name": "click", "arguments": {"pageId": 3, "uid": checkbox_uid}}
        })
        recv(7)
        time.sleep(1)

        # Click Final Submit
        send({
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {"name": "click", "arguments": {"pageId": 3, "uid": dialog_submit_uid}}
        })
        res8 = recv(8)
        print("Submission clicked! Response:", res8)
        time.sleep(3)

        # Verification Snapshot
        send({
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {"name": "take_snapshot", "arguments": {"pageId": 3}}
        })
        res9 = recv(9)
        snap3 = res9.get("result", {}).get("content", [{}])[0].get("text", "")
        print("\n--- OUTCOME STATUS ---")
        for line in snap3.splitlines()[:25]:
            if any(k in line.lower() for k in ["submitted", "success", "error", "can't", "minutes", "clip"]):
                print("  ", line)

        return True

    finally:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    # Test submission on GTA VI Clipup Campaign
    clipup_url = "https://contentrewards.com/c/campaigns/802cf95a-ea84-4070-9a96-8a917831cb16"
    test_clip = "https://www.youtube.com/shorts/3DpGGtfEHF4"
    run_submission_on_tab3(clipup_url, test_clip)
