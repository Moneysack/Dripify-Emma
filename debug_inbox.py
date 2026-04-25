"""Debug: Login + inspect inbox conversation list structure"""
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

print("Going to:", BASE)
page.goto(BASE, wait_until="domcontentloaded", timeout=30000)
time.sleep(3)

# Dismiss Cookiebot
for sel in [
    '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll',
    'button:has-text("Allow all")',
    'button:has-text("Accept All")',
]:
    try:
        btn = page.wait_for_selector(sel, timeout=4000)
        if btn and btn.is_visible():
            btn.click()
            print(f"Cookiebot dismissed via: {sel}")
            time.sleep(2)
            break
    except Exception:
        pass

# Fill credentials
page.wait_for_selector('input[type="email"]', timeout=8000)
page.fill('input[type="email"]', EMAIL)
page.fill('input[type="password"]', PASSWORD)
page.click('button[type="submit"]')
print("Submitted login...")

# Wait for redirect
page.wait_for_function(
    "() => !window.location.href.endsWith('app.dripify.com/') && "
    "       !window.location.href.includes('sign-in') && "
    "       window.location.href.includes('dripify.com')",
    timeout=30000
)
time.sleep(4)
print("Logged in:", page.url)

# Navigate to inbox
page.goto(f"{BASE}/inbox", wait_until="networkidle", timeout=30000)
time.sleep(5)
page.screenshot(path="inbox_debug.png")
print("inbox_debug.png saved — URL:", page.url)

# ── Find the conversation list ─────────────────────────────────────────────────
# Dripify inbox: conversation list is in the main content, not aside
# Try to find elements that look like contact/person list items
print("\n-- Scanning for conversation-list items --")

# Strategy: find any element containing a name that also has avatar/image nearby
# Look at children of main, article, div[class*="main"], etc.
js_result = page.evaluate("""() => {
    // Try to find the conversation list container
    const candidates = [
        '[class*="conversations"]',
        '[class*="Conversations"]',
        '[class*="chat-list"]',
        '[class*="ChatList"]',
        '[class*="inbox"]',
        '[class*="Inbox"]',
        'main',
        '[role="main"]',
        '.content',
        '[class*="content"]',
    ];

    const results = {};
    for (const sel of candidates) {
        const el = document.querySelector(sel);
        if (el) {
            results[sel] = {
                tag: el.tagName,
                cls: el.className.substring(0, 80),
                childCount: el.children.length,
                html: el.outerHTML.substring(0, 300),
            };
        }
    }
    return results;
}""")

for sel, info in js_result.items():
    print(f"  {sel} -> <{info['tag']} class='{info['cls']}'> ({info['childCount']} children)")

# ── Dump ALL clickable/interactive elements that might be conversation rows ────
print("\n-- Clickable elements (buttons, links, divs with click handlers) --")
clickable = page.query_selector_all("a[href], button, [role='button'], [role='listitem'], [role='option']")
shown = 0
for el in clickable:
    try:
        txt = el.inner_text().strip()[:60].replace("\n", " ")
        cls = (el.get_attribute("class") or "")[:60]
        href = el.get_attribute("href") or ""
        if txt and len(txt) > 2 and "aside" not in cls and "nav" not in cls.lower():
            print(f"  [{el.evaluate('e => e.tagName')}] class='{cls}' href='{href}' -> '{txt}'")
            shown += 1
            if shown >= 60:
                print("  ...(more)")
                break
    except Exception:
        pass

# ── Save full main content HTML ────────────────────────────────────────────────
html = page.evaluate("""() => {
    // Get everything EXCEPT the aside nav
    const aside = document.querySelector('aside');
    if (aside) aside.remove();
    return document.body.innerHTML.substring(0, 20000);
}""")
Path("inbox_content.html").write_text(html, encoding="utf-8")
print("\ninbox_content.html saved (first 20000 chars of body without nav aside)")

# Also try to find elements with LinkedIn-like name patterns
print("\n-- Elements with 2+ words of text (likely person names) --")
all_spans = page.query_selector_all("span, p, div, h1, h2, h3, h4, h5")
shown2 = 0
for el in all_spans:
    try:
        txt = el.inner_text().strip()
        kids = el.evaluate("e => e.children.length")
        cls = (el.get_attribute("class") or "")
        # Looking for person names: 2 words, capitalized, no special chars
        words = txt.split()
        if (2 <= len(words) <= 4 and kids == 0 and
            all(w[0].isupper() for w in words if w) and
            len(txt) < 40 and
            not any(c in txt for c in ['<', '>', '{', '}', '(', ')'])):
            tag = el.evaluate("e => e.tagName.toLowerCase()")
            print(f"  <{tag} class='{cls[:60]}'> -> '{txt}'")
            shown2 += 1
            if shown2 >= 50:
                print("  ...(more)")
                break
    except Exception:
        pass

print("\nDone. Check inbox_debug.png and inbox_content.html")
browser.close()
pw.stop()
