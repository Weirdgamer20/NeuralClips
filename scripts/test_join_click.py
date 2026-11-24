from playwright.sync_api import sync_playwright

def click_join():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = "https://contentrewards.com/c/campaigns/1d2bcb00-c904-415f-aa82-f95b96baad86"
        page.goto(url, wait_until="networkidle")
        
        # Click Join Campaign
        join_btn = page.locator("button:has-text('Join Campaign')").first
        if join_btn:
            print("Clicking Join Campaign...")
            join_btn.click()
            page.wait_for_timeout(3000)
            print("After click URL:", page.url)
            # Check modal or text
            text = page.inner_text("body")
            print("Body snippet after click:")
            for line in [l.strip() for l in text.split("\n") if l.strip()][:25]:
                print("  ", line)
        browser.close()

if __name__ == "__main__":
    click_join()
