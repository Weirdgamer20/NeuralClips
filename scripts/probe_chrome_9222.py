import urllib.request

for p in ["/", "/devtools", "/json", "/json/version", "/json/list", "/json/protocol", "/inspect"]:
    try:
        r = urllib.request.urlopen(f"http://127.0.0.1:9222{p}")
        print(f"Path {p}: {r.status} {r.read().decode('utf-8')[:100]}")
    except urllib.error.HTTPError as e:
        print(f"Path {p}: HTTP {e.code}")
    except Exception as e:
        print(f"Path {p}: {e}")
