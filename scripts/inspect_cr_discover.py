from playwright.sync_api import sync_playwright

def inspect_discover():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to https://contentrewards.com/c/discover ...")
        page.goto("https://contentrewards.com/c/discover", wait_until="networkidle")
        print("URL:", page.url)
        print("Title:", page.title())
        # Grab text
        text = page.inner_text("body")
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        print(f"Total lines: {len(lines)}")
        print("\n--- SAMPLE CONTENT (First 30 lines) ---")
        for line in lines[:30]:
            print(line)
        browser.close()

if __name__ == "__main__":
    inspect_discover()
