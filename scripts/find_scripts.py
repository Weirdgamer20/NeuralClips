import urllib.request
import re

req = urllib.request.Request('https://contentrewards.com/c/discover', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')
scripts = re.findall(r'<script[^>]+src=[\'"]([^\'"]+)[\'"]', html)
for s in scripts[:10]:
    print(s)
