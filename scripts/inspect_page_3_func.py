import subprocess
import json

def inspect_page_3():
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

    while True:
        line = p.stdout.readline()
        if not line or json.loads(line).get("id") == 1:
            break

    js_func = """() => {
        const buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean);
        const inputs = Array.from(document.querySelectorAll('input')).map(i => ({placeholder: i.placeholder, name: i.name, type: i.type, value: i.value}));
        const userMenu = document.querySelector('[aria-label*="user"], [aria-label*="account"], [aria-label*="profile"]');
        return {
            title: document.title,
            url: window.location.href,
            buttons: buttons,
            inputs: inputs,
            hasJoinButton: buttons.some(b => b.toLowerCase().includes('join')),
            hasSubmitButton: buttons.some(b => b.toLowerCase().includes('submit'))
        };
    }"""

    send({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "evaluate_script",
            "arguments": {
                "pageId": 3,
                "function": js_func,
                "waitForStableDom": False
            }
        }
    })

    while True:
        line = p.stdout.readline()
        if not line:
            break
        msg = json.loads(line)
        if msg.get("id") == 2:
            print("RESULT FROM CHROME TAB:")
            res = msg.get("result", {})
            for c in res.get("content", []):
                print(c.get("text"))
            break

    p.terminate()

if __name__ == "__main__":
    inspect_page_3()
