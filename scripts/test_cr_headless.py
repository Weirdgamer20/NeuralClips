from playwright.sync_api import sync_playwright

def test_fetch():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to https://contentrewards.com...")
        page.goto("https://contentrewards.com", wait_until="networkidle")
        print("Page title:", page.title())
        print("Current URL:", page.url)
        # Check text or elements
        text = page.inner_text("body")
        print("Text snippet:", text[:500].replace('\n', ' '))
        browser.close()

if __name__ == "__main__":
    test_fetch()
