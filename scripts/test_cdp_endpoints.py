import urllib.request
import json

for ep in ["/json/version", "/json", "/json/list", "/"]:
    try:
        url = f"http://127.0.0.1:9222{ep}"
        req = urllib.request.Request(url, headers={"Host": "localhost"})
        res = urllib.request.urlopen(req)
        print(f"SUCCESS {ep}: {res.status}")
        print(res.read().decode("utf-8")[:300])
    except Exception as e:
        print(f"FAIL {ep}: {e}")
