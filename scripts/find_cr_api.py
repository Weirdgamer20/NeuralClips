import urllib.request
import re
import json

def find_api_routes():
    req = urllib.request.Request("https://contentrewards.com/c/discover", headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req).read().decode("utf-8")
    
    # Find all script src
    scripts = re.findall(r'src="(/_next/static/chunks/[^"]+)"', html)
    print(f"Found {len(scripts)} script chunks.")
    
    routes = set()
    for s in scripts[:15]:
        s_url = "https://contentrewards.com" + s
        try:
            s_req = urllib.request.Request(s_url, headers={"User-Agent": "Mozilla/5.0"})
            js = urllib.request.urlopen(s_req).read().decode("utf-8")
            
            # Look for api endpoints
            found = re.findall(r'["\'](/api/[^"\']+)["\']', js)
            routes.update(found)
            
            # Look for submission or clip endpoints
            subs = re.findall(r'["\']([^"\']*(?:submission|submit|clip)[^"\']*)["\']', js, re.I)
            for sub in subs:
                if "/" in sub and len(sub) < 50:
                    routes.add(sub)
        except Exception as e:
            pass
            
    print("Discovered routes/endpoints:")
    for r in sorted(routes):
        print("  ", r)

if __name__ == "__main__":
    find_api_routes()
