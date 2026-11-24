import urllib.request
import re

req = urllib.request.Request('https://contentrewards.com/c/discover', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')
scripts = re.findall(r'<script[^>]+src=[\'"]([^\'"]+)[\'"]', html)

for s in scripts:
    try:
        js = urllib.request.urlopen(urllib.request.Request(s, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8')
        if "submit" in js.lower() or "submission" in js.lower():
            # Find api endpoints or patterns
            matches = set(re.findall(r'["\'](/api/[^"\']+)["\']', js))
            if matches:
                print(f"From {s}:")
                for m in matches:
                    print("  ", m)
    except Exception:
        pass
