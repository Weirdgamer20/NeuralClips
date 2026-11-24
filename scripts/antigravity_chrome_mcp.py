"""
Antigravity Chrome MCP Bridge
=============================
Author: Antigravity AI
Workspace: NeuralClips repository

Direct programmatic control of Google Chrome through Chrome DevTools MCP.
Automatically detects running Chrome with remote debugging on port 9222.

Capabilities:
- list_pages: Lists all active Chrome tabs with IDs, titles, and URLs.
- take_snapshot: Captures accessibility tree and element UIDs.
- click: Clicks elements by UID.
- fill: Types / pastes values into inputs by UID.
- evaluate: Executes arbitrary JavaScript in any open tab.
- auto_submit: Submits YouTube Short URLs to joined Content Rewards campaigns.
"""

import subprocess
import json
import time
import sys
from pathlib import Path

def call_mcp(tool_name: str, arguments: dict = None, timeout: int = 15) -> dict:
    """Executes an atomic Chrome DevTools MCP command and safely releases resources."""
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

    try:
        # 1. Initialize MCP Handshake
        send({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "antigravity-ai", "version": "2.0"}
            }
        })

        while True:
            line = p.stdout.readline()
            if not line:
                return {"error": "MCP handshake timed out or failed to connect"}
            msg = json.loads(line)
            if msg.get("id") == 1:
                break

        # 2. Complete Initialization
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})

        # 3. Call Specified Tool
        send({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        })

        while True:
            line = p.stdout.readline()
            if not line:
                return {"error": "No response received from Chrome DevTools"}
            msg = json.loads(line)
            if msg.get("id") == 2:
                return msg.get("result", {})

    finally:
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

def list_tabs():
    """Returns list of open Chrome tabs: [{'id': int, 'title': str, 'url': str}]"""
    res = call_mcp("list_pages")
    text = res.get("content", [{}])[0].get("text", "")
    tabs = []
    for line in text.splitlines():
        line = line.strip()
        if line and line[0].isdigit() and ":" in line:
            parts = line.split(":", 1)
            try:
                pid = int(parts[0])
                tabs.append({"id": pid, "info": parts[1].strip()})
            except Exception:
                pass
    return tabs

def get_page_snapshot(page_id: int):
    """Returns accessibility snapshot string for a given tab ID."""
    res = call_mcp("take_snapshot", {"pageId": page_id})
    return res.get("content", [{}])[0].get("text", "")

def click(page_id: int, uid: str):
    """Clicks an element in the given tab by its snapshot UID."""
    return call_mcp("click", {"pageId": page_id, "uid": uid})

def fill(page_id: int, uid: str, text: str):
    """Fills an input element in the given tab by its snapshot UID."""
    return call_mcp("fill", {"pageId": page_id, "uid": uid, "value": text})

def navigate(page_id: int, url: str):
    """Navigates an existing tab to a target URL."""
    return call_mcp("navigate_page", {"pageId": page_id, "url": url})

def evaluate(page_id: int, js_func: str):
    """Executes a JS function inside the target page."""
    return call_mcp("evaluate_script", {
        "pageId": page_id,
        "function": js_func,
        "waitForStableDom": False
    })

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "list"

    if action == "list":
        print("=" * 60)
        print("🌐 Antigravity AI :: Live Chrome Tabs")
        print("=" * 60)
        tabs = list_tabs()
        for t in tabs:
            print(f"  Tab [{t['id']}]: {t['info']}")
        print()

    elif action == "snapshot" and len(sys.argv) > 2:
        pid = int(sys.argv[2])
        print(f"📸 Snapshot of Tab [{pid}]:")
        print(get_page_snapshot(pid))

    elif action == "click" and len(sys.argv) > 3:
        pid = int(sys.argv[2])
        uid = sys.argv[3]
        print(f"🖱️ Clicking element {uid} on Tab [{pid}]...")
        res = click(pid, uid)
        print(res)

    elif action == "navigate" and len(sys.argv) > 3:
        pid = int(sys.argv[2])
        url = sys.argv[3]
        print(f"🚀 Navigating Tab [{pid}] to {url}...")
        res = navigate(pid, url)
        print(res)

    else:
        print("Usage:")
        print("  python scripts/antigravity_chrome_mcp.py list")
        print("  python scripts/antigravity_chrome_mcp.py snapshot <page_id>")
        print("  python scripts/antigravity_chrome_mcp.py click <page_id> <uid>")
        print("  python scripts/antigravity_chrome_mcp.py navigate <page_id> <url>")
