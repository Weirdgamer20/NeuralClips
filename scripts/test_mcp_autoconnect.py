import subprocess
import time

p = subprocess.Popen(
    ["npx.cmd", "-y", "chrome-devtools-mcp@latest", "--autoConnect"],
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    stdin=subprocess.PIPE,
    text=True
)
time.sleep(3)
p.terminate()
stdout, stderr = p.communicate()
print("STDOUT:", stdout[:500])
print("STDERR:", stderr[:500])
