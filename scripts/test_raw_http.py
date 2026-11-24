import http.client

conn = http.client.HTTPConnection("127.0.0.1", 9222)
conn.request("GET", "/json/version")
r = conn.getresponse()
print("Status:", r.status, r.reason)
print("Headers:", r.getheaders())
print("Body:", r.read().decode("utf-8", errors="ignore"))
