import urllib.request
import json

try:
    res = urllib.request.urlopen("http://127.0.0.1:9222/json/list")
    tabs = json.loads(res.read().decode("utf-8"))
    print(f"Total tabs/targets found: {len(tabs)}")
    for i, t in enumerate(tabs, 1):
        t_type = t.get("type", "unknown")
        title = t.get("title", "")
        url = t.get("url", "")
        ws = t.get("webSocketDebuggerUrl", "")
        print(f"[{i}] Type: {t_type} | Title: {title}")
        print(f"    URL: {url}")
        print(f"    WebSocket: {ws}")
except Exception as e:
    print("Error querying Chrome debugging port:", e)
