from playwright.sync_api import sync_playwright

try:
    with sync_playwright() as p:
        print("Connecting to Chrome over CDP on 127.0.0.1:9222...")
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        print("Connected successfully!")
        contexts = browser.contexts
        print(f"Contexts: {len(contexts)}")
        for i, ctx in enumerate(contexts):
            print(f"Context {i} pages: {len(ctx.pages)}")
            for j, page in enumerate(ctx.pages):
                print(f"  Page {j}: Title='{page.title()}' URL='{page.url}'")
except Exception as e:
    print("CDP Connection Error:", e)
