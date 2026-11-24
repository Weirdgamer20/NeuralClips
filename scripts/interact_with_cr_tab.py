import subprocess
import json

def inspect_cr_tab():
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

    # 1. Initialize
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

    # 2. Call evaluate_script on pageId 3
    # Look for Join button, submit input, or user status
    js_code = """
    (() => {
        const buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(Boolean);
        const inputs = Array.from(document.querySelectorAll('input')).map(i => ({placeholder: i.placeholder, type: i.type, value: i.value}));
        const links = Array.from(document.querySelectorAll('a')).map(a => ({text: a.innerText.trim(), href: a.href})).filter(a => a.text);
        return {
            title: document.title,
            url: window.location.href,
            buttons: buttons,
            inputs: inputs,
            links: links.slice(0, 15)
        };
    })()
    """

    send({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "evaluate_script",
            "arguments": {
                "pageId": 3,
                "expression": js_code
            }
        }
    })

    while True:
        line = p.stdout.readline()
        if not line:
            break
        msg = json.loads(line)
        if msg.get("id") == 2:
            print("CR TAB INSPECTION RESULT:")
            print(json.dumps(msg, indent=2))
            break

    p.terminate()

if __name__ == "__main__":
    inspect_cr_tab()
