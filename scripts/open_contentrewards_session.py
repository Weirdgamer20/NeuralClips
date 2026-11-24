"""
Content Rewards Safe Automation Session
Launches a visible Chromium session with a persistent profile.
Allows user to log in safely. Inspects active campaigns and submitted clips.
Explicitly blocks access to any wallet, payout, or banking pages.
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

USER_DATA_DIR = Path(str(BASE_DIR / "storage" / "contentrewards_profile"))
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

BLOCKED_KEYWORDS = ["wallet", "payout", "withdraw", "bank", "billing", "payment-method"]

def check_url_allowed(url: str) -> bool:
    url_lower = url.lower()
    for kw in BLOCKED_KEYWORDS:
        if kw in url_lower:
            return False
    return True

def main():
    print("=" * 60)
    print("🚀 Launching Content Rewards Safe Browser Session")
    print(f"📁 Session Profile: {USER_DATA_DIR}")
    print("🔒 Safety Rule: Wallet and payout pages are strictly blocked.")
    print("=" * 60)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--start-maximized"]
        )

        page = context.pages[0] if context.pages else context.new_page()

        # Intercept routing to prevent any accidental navigation to wallet/payout
        def handle_route(route):
            req_url = route.request.url.lower()
            if not check_url_allowed(req_url):
                print(f"⛔ [SAFETY BLOCKED] Prevented access to: {req_url}")
                route.abort()
            else:
                route.continue_()

        context.route("**/*", handle_route)

        print("🌐 Navigating to https://contentrewards.com ...")
        page.goto("https://contentrewards.com", wait_until="domcontentloaded")
        print("\n✅ Browser is now open on your screen!")
        print("👉 Please log in to your Content Rewards account in the open window.")
        print("⏳ Waiting for login... (You can take your time to sign in)")

        # Wait loop to let the user log in
        logged_in = False
        for _ in range(300): # Wait up to 5 minutes
            time.sleep(2)
            current_url = page.url
            # Check if user has navigated past login / to dashboard
            if "contentrewards.com" in current_url and not any(k in current_url.lower() for k in ["login", "sign-in", "auth"]):
                # Inspect for user indicators
                try:
                    title = page.title()
                    # Check for logged-in indicators
                    content = page.content()
                    if "dashboard" in current_url.lower() or "campaigns" in current_url.lower() or "my-clips" in content.lower():
                        logged_in = True
                        print(f"\n🎉 Detected active logged-in session! URL: {current_url}")
                        break
                except Exception:
                    pass

        print("\nSession remains open. Close the browser window when you are done.")
        # Keep alive while page is not closed
        try:
            while not page.is_closed():
                time.sleep(1)
        except Exception:
            pass

        context.close()
        print("Browser closed. Session state saved to storage/contentrewards_profile.")

if __name__ == "__main__":
    main()
