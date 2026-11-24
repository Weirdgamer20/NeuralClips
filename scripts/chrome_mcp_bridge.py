import subprocess
import json
import atexit

class ChromeMCPBridge:
    def __init__(self):
        self.proc = subprocess.Popen(
            ["npx.cmd", "-y", "chrome-devtools-mcp@latest", "--autoConnect"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True,
            bufsize=1
        )
        self.req_id = 0
        atexit.register(self.close)
        self._init()

    def _send(self, obj):
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def _recv(self, target_id=None):
        while True:
            line = self.proc.stdout.readline()
            if not line:
                return None
            try:
                msg = json.loads(line)
                if target_id is None or msg.get("id") == target_id:
                    return msg
            except Exception:
                continue

    def _init(self):
        self.req_id += 1
        self._send({
            "jsonrpc": "2.0",
            "id": self.req_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "antigravity-ai", "version": "1.0"}
            }
        })
        self._recv(self.req_id)
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def call_tool(self, name, arguments=None):
        self.req_id += 1
        self._send({
            "jsonrpc": "2.0",
            "id": self.req_id,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments or {}
            }
        })
        return self._recv(self.req_id)

    def list_pages(self):
        res = self.call_tool("list_pages")
        if not res or "result" not in res:
            return []
        text = res["result"].get("content", [{}])[0].get("text", "")
        pages = []
        for line in text.splitlines():
            line = line.strip()
            if line and line[0].isdigit() and ":" in line:
                parts = line.split(":", 1)
                pid = int(parts[0])
                rest = parts[1].strip()
                pages.append({"id": pid, "info": rest})
        return pages

    def evaluate(self, page_id, js_func):
        res = self.call_tool("evaluate_script", {
            "pageId": page_id,
            "function": js_func,
            "waitForStableDom": False
        })
        return res

    def close(self):
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except Exception:
                self.proc.kill()

if __name__ == "__main__":
    bridge = ChromeMCPBridge()
    try:
        pages = bridge.list_pages()
        print("--- OPEN CHROME TABS ---")
        for p in pages:
            print(f"[{p['id']}] {p['info']}")
            
        # Find Content Rewards tab
        cr_page = next((p for p in pages if "contentrewards.com" in p["info"].lower()), None)
        if cr_page:
            print(f"\n🔍 Inspecting Content Rewards tab (Page ID: {cr_page['id']})...")
            inspect_func = """() => {
                const buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean);
                const cards = Array.from(document.querySelectorAll('a[href*="/c/"]')).map(a => ({text: a.innerText.trim().replace(/\\n+/g, ' | '), href: a.href}));
                return {
                    title: document.title,
                    url: window.location.href,
                    buttons: buttons.slice(0, 10),
                    campaigns: cards.slice(0, 10)
                };
            }"""
            res = bridge.evaluate(cr_page["id"], inspect_func)
            print("Tab details:", json.dumps(res, indent=2))
    finally:
        bridge.close()
