"""
Debug: Open a Dripify conversation and dump the right-panel HTML + test profile selectors.
Run: python debug_profile_panel.py
Outputs: profile_panel.html  (right panel DOM)
         profile_screenshot.png
"""
import sys, time, json
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, ".")

# Load credentials from session or env
from config import settings  # type: ignore
EMAIL    = settings.dripify_email
PASSWORD = settings.dripify_password
BASE     = "https://app.dripify.com"
SESSION  = Path("dripify_session.json")

pw      = sync_playwright().start()
browser = pw.chromium.launch(headless=False)
storage = {}
if SESSION.exists():
    try:
        storage = json.loads(SESSION.read_text())
    except Exception:
        pass

ctx = browser.new_context(
    storage_state=storage if storage else None,
    viewport={"width": 1440, "height": 900},
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
)
page = ctx.new_page()

# ── Login if needed ──────────────────────────────────────────────────────────
page.goto(BASE, wait_until="domcontentloaded", timeout=30_000)
time.sleep(3)

for sel in ["#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
            'button:has-text("Allow all")', 'button:has-text("Accept All")']:
    try:
        btn = page.wait_for_selector(sel, timeout=3000)
        if btn and btn.is_visible():
            btn.click(); time.sleep(2); break
    except Exception:
        pass

if any(x in page.url for x in ["sign-in", "login", "auth", "app.dripify.com/"]):
    print("Logging in...")
    page.fill('input[type="email"]', EMAIL)
    page.fill('input[type="password"]', PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_function(
        "() => !window.location.href.endsWith('app.dripify.com/') && "
        "!window.location.href.includes('sign-in') && "
        "window.location.href.includes('dripify.com')",
        timeout=30_000,
    )
    time.sleep(3)
    SESSION.write_text(json.dumps(ctx.storage_state()))
    print("Login done, session saved.")

# ── Open inbox and click first conversation ──────────────────────────────────
page.goto(f"{BASE}/inbox", wait_until="networkidle", timeout=30_000)
time.sleep(5)

items = page.query_selector_all("a.chats-list__item")
print(f"Found {len(items)} conversation items")
if not items:
    page.screenshot(path="profile_screenshot.png")
    print("No items found. Screenshot saved.")
    browser.close(); pw.stop(); sys.exit(1)

# Click first item
href  = items[0].get_attribute("href") or ""
name_el = items[0].query_selector("div.chat-item__name")
name  = name_el.inner_text().strip() if name_el else "?"
conv_id = href.split("/inbox/")[-1] if "/inbox/" in href else "?"
print(f"Opening: {name} (id={conv_id})")
page.goto(f"{BASE}{href}", wait_until="domcontentloaded", timeout=30_000)
time.sleep(4)

page.screenshot(path="profile_screenshot.png")
print("profile_screenshot.png saved")

# ── Dump entire right panel HTML ─────────────────────────────────────────────
panel_html = page.evaluate("""() => {
    const tries = [
        '.messages__lead-card',
        '.messages__lead',
        '[class*="lead-card"]',
        '[class*="LeadCard"]',
        '[class*="lead-info"]',
        '[class*="profile"]',
        '.right-panel',
        '[class*="right"]',
        'aside',
    ];
    for (const s of tries) {
        const el = document.querySelector(s);
        if (el && el.innerHTML.length > 100) {
            return '<!-- SELECTOR: ' + s + ' -->\\n' + el.outerHTML;
        }
    }
    return '<!-- fallback: full body -->\\n' + document.body.innerHTML.substring(0, 40000);
}""")

Path("profile_panel.html").write_text(panel_html, encoding="utf-8")
print("profile_panel.html saved — inspect this to find the right selectors")

# ── Test our current selectors ───────────────────────────────────────────────
PROFILE_SELS = {
    "title": [
        ".messages__lead-card .lead-info__title",
        ".messages__lead-card [class*='title']",
        ".lead-card [class*='position']",
        ".lead-card [class*='title']",
        "[class*='lead'] [class*='position']",
        "[class*='lead'] [class*='headline']",
    ],
    "company_name": [
        ".messages__lead-card .lead-info__company",
        ".messages__lead-card [class*='company']",
        ".lead-card [class*='company']",
        "[class*='lead'] [class*='company']",
    ],
    "location": [
        ".messages__lead-card .lead-info__location",
        ".messages__lead-card [class*='location']",
        ".lead-card [class*='location']",
        "[class*='lead'] [class*='location']",
        "[class*='lead'] [class*='city']",
    ],
    "email": [
        ".messages__lead-card a[href^='mailto:']",
        ".lead-card a[href^='mailto:']",
        "[class*='lead'] a[href^='mailto:']",
        "a[href^='mailto:']",
    ],
    "connections_count": [
        ".messages__lead-card [class*='connection']",
        ".lead-card [class*='connection']",
        "[class*='lead'] [class*='connection']",
        "[class*='connection']",
        "[class*='follower']",
    ],
    "linkedin_url": [
        ".messages__lead-card a[href*='linkedin.com']",
        ".lead-card a[href*='linkedin.com']",
        "[class*='lead'] a[href*='linkedin.com/in/']",
        "a[href*='linkedin.com/in/']",
    ],
}

print("\n── Testing selectors ──")
for field, sels in PROFILE_SELS.items():
    found = False
    for sel in sels:
        try:
            el = page.query_selector(sel)
            if el:
                if field in ("linkedin_url", "email"):
                    href_val = el.get_attribute("href") or ""
                    val = href_val.replace("mailto:", "").strip() if field == "email" else href_val
                else:
                    val = (el.inner_text() or "").strip()
                if val:
                    print(f"  ✓ {field}: '{val[:60]}' (via: {sel})")
                    found = True
                    break
        except Exception:
            continue
    if not found:
        print(f"  ✗ {field}: NOT FOUND")

# ── Also dump ALL elements whose class contains useful keywords ───────────────
print("\n── All elements with relevant class names ──")
found_classes = page.evaluate("""() => {
    const keywords = ['lead', 'profile', 'contact', 'title', 'company', 'position',
                      'location', 'city', 'email', 'connection', 'headline', 'info'];
    const results = [];
    const seen = new Set();
    document.querySelectorAll('[class]').forEach(el => {
        const cls = el.className || '';
        if (typeof cls !== 'string') return;
        const lc = cls.toLowerCase();
        if (keywords.some(k => lc.includes(k))) {
            const key = cls.substring(0, 80);
            if (!seen.has(key)) {
                seen.add(key);
                results.push({
                    tag: el.tagName,
                    cls: cls.substring(0, 100),
                    text: (el.innerText || '').trim().substring(0, 60),
                    href: el.getAttribute('href') || '',
                });
            }
        }
    });
    return results.slice(0, 60);
}""")

for item in found_classes:
    print(f"  <{item['tag']} class='{item['cls']}'> href='{item['href']}' -> '{item['text']}'")

# ── Also find the textarea and send button ────────────────────────────────────
print("\n── Textarea / send button test ──")
TEXTAREA_SELS = [
    "div.chat-footer textarea",
    "textarea.message-input",
    "textarea[placeholder]",
    ".chat-input textarea",
    "[class*='footer'] textarea",
    "[class*='input'] textarea",
    "textarea",
]
for sel in TEXTAREA_SELS:
    try:
        el = page.query_selector(sel)
        if el and el.is_visible():
            print(f"  ✓ Textarea found: {sel}")
            break
    except Exception:
        continue
else:
    print("  ✗ No textarea found")

SEND_SELS = [
    "button.send-btn",
    "button[class*='send']",
    "[class*='footer'] button:last-child",
    "[class*='chat'] button[type='submit']",
    "button[aria-label*='send' i]",
]
for sel in SEND_SELS:
    try:
        el = page.query_selector(sel)
        if el and el.is_visible():
            print(f"  ✓ Send button found: {sel}")
            break
    except Exception:
        continue
else:
    print("  ✗ No send button found")

print("\nDone. Check profile_panel.html to fix any missing selectors.")
browser.close()
pw.stop()
