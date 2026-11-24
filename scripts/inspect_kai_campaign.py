from playwright.sync_api import sync_playwright

def inspect_kai_campaign():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = "https://contentrewards.com/c/campaigns/1d2bcb00-c904-415f-aa82-f95b96baad86"
        page.goto(url, wait_until="networkidle")
        text = page.inner_text("body")
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        print("Campaign lines:")
        for line in lines[:40]:
            print("  ", line)
        browser.close()

if __name__ == "__main__":
    inspect_kai_campaign()
