"""Debug: Navigate to one conversation and inspect message structure"""
import sys, time
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright
from pathlib import Path

EMAIL    = "bbannier@einoworld.com"
PASSWORD = "XwcZV7ZN_N&mR3_"
BASE     = "https://app.dripify.com"

pw      = sync_playwright().start()
browser = pw.chromium.launch(headless=False)
context = browser.new_context(
    viewport={"width": 1440, "height": 900},
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
)
page = context.new_page()

page.goto(BASE, wait_until="domcontentloaded", timeout=30000)
time.sleep(3)

# Dismiss Cookiebot
try:
    btn = page.wait_for_selector('#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll', timeout=5000)
    if btn and btn.is_visible():
        btn.click()
        time.sleep(2)
except Exception:
    pass

# Login
page.fill('input[type="email"]', EMAIL)
page.fill('input[type="password"]', PASSWORD)
page.click('button[type="submit"]')
page.wait_for_function(
    "() => !window.location.href.endsWith('app.dripify.com/') && window.location.href.includes('dripify.com')",
    timeout=30000
)
time.sleep(3)
print("Logged in:", page.url)

# Go to inbox
page.goto(f"{BASE}/inbox", wait_until="networkidle", timeout=30000)
time.sleep(4)

# Get all conversation items
items = page.query_selector_all("a.chats-list__item")
print(f"Found {len(items)} conversation items")

if not items:
    print("No items found!")
    browser.close(); pw.stop(); sys.exit(1)

# Click first conversation
first = items[0]
name_el = first.query_selector("div.chat-item__name")
name = name_el.inner_text().strip() if name_el else "Unknown"
href = first.get_attribute("href")
conv_id = href.split("/inbox/")[-1] if href else "?"
print(f"\nOpening: {name} (id={conv_id})")

first.click()
time.sleep(3)
page.screenshot(path="conversation_debug.png")
print("conversation_debug.png saved")

# Save message area HTML
html = page.evaluate("""() => {
    const tries = [
        '[class*="messages-list"]',
        '[class*="MessagesList"]',
        '[class*="chat-messages"]',
        '[class*="ChatMessages"]',
        '[class*="conversation"]',
        '[class*="message-list"]',
        '.messages__chat',
        '.messages__content',
        'main',
    ];
    for (const s of tries) {
        const el = document.querySelector(s);
        if (el && el.innerHTML.length > 200)
            return '<!-- ' + s + ' -->\\n' + el.outerHTML.substring(0, 20000);
    }
    return document.body.innerHTML.substring(0, 20000);
}""")
Path("conversation_debug.html").write_text(html, encoding="utf-8")
print("conversation_debug.html saved")

# Print all elements with message-like text
print("\n-- All classes containing 'message' or 'chat' or 'bubble' --")
all_els = page.query_selector_all("[class]")
seen_classes = set()
for el in all_els:
    try:
        cls = (el.get_attribute("class") or "").lower()
        if any(k in cls for k in ["message", "bubble", "chat-item", "msg-"]):
            cls_short = el.get_attribute("class")[:80]
            tag = el.evaluate("e => e.tagName.toLowerCase()")
            txt = el.inner_text().strip()[:60].replace("\n", " ")
            key = cls_short[:40]
            if key not in seen_classes:
                seen_classes.add(key)
                print(f"  <{tag} class='{cls_short}'> -> '{txt}'")
    except Exception:
        pass

browser.close()
pw.stop()
