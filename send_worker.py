"""
Send Worker — läuft lokal im Hintergrund.
Sendet alle 60 Sekunden ausstehende Nachrichten aus der pending_sends Queue.

Start: python send_worker.py
"""
from __future__ import annotations
import json, logging, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("send_worker")

from config import settings
from database.client import get_db

EMAIL    = settings.dripify_email
PASSWORD = settings.dripify_password
BASE     = "https://app.dripify.com"
INTERVAL = 60  # Sekunden zwischen Checks

TEXTAREA_SELS = [
    "textarea[placeholder]",
    "div.chat-footer textarea",
    "textarea.message-input",
    ".chat-input textarea",
    "textarea",
]
SEND_BTN_SELS = [
    "button[class*='send']",
    "button.send-btn",
    "[class*='footer'] button:last-child",
    "button[aria-label*='send' i]",
]


def get_browser_page():
    """Start Playwright, login, return (pw, browser, page)."""
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
    )
    ctx = browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
    )
    page = ctx.new_page()

    log.info("Logging in as %s ...", EMAIL)
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

    page.fill('input[type="email"]', EMAIL)
    page.fill('input[type="password"]', PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_function(
        "() => window.location.href.includes('dripify.com') && "
        "      !window.location.href.includes('sign-in')",
        timeout=30_000,
    )
    time.sleep(3)
    Path("dripify_session.json").write_text(json.dumps(ctx.storage_state()))
    log.info("Login OK: %s", page.url)
    return pw, browser, ctx, page


def send_one(page, did: str, text: str) -> bool:
    page.goto(f"{BASE}/inbox/{did}", wait_until="domcontentloaded", timeout=30_000)
    time.sleep(4)

    if any(x in page.url for x in ["sign-in", "login", "auth"]):
        log.warning("Redirected to login during send!")
        return False

    ta = None
    for sel in TEXTAREA_SELS:
        try:
            from playwright.sync_api import TimeoutError as PWTimeout
            el = page.wait_for_selector(sel, timeout=5000)
            if el and el.is_visible():
                ta = el; break
        except Exception:
            continue

    if not ta:
        log.error("Textarea not found for %s", did[:20])
        return False

    ta.click(); time.sleep(0.3)
    ta.fill(text); time.sleep(0.5)

    sent = False
    for sel in SEND_BTN_SELS:
        try:
            btn = page.query_selector(sel)
            if btn and btn.is_visible() and btn.is_enabled():
                btn.click(); sent = True; break
        except Exception:
            continue
    if not sent:
        ta.press("Enter")

    time.sleep(2)
    return True


def drain_queue(page, db):
    pending = db.table("pending_sends").select("*") \
        .in_("status", ["pending", "failed"]).execute().data

    if not pending:
        return 0

    log.info("Queue: %d Nachricht(en) zum Senden", len(pending))
    sent_count = 0

    for p in pending:
        did  = p.get("dripify_contact_id", "")
        text = p.get("text", "")
        pid  = p["id"]

        if not did or not text:
            continue

        log.info("  Sende: %s", repr(text[:50]))
        ok = send_one(page, did, text)

        if ok:
            db.table("pending_sends").update({"status": "sent", "sent_at": "now()"}).eq("id", pid).execute()
            try:
                db.table("messages").update({"sent_to_dripify": True}) \
                    .eq("contact_id", p["contact_id"]).eq("text", text).eq("direction", "outgoing").execute()
            except Exception:
                pass
            log.info("  ✓ Gesendet")
            sent_count += 1
        else:
            db.table("pending_sends").update({"status": "failed", "error_msg": "Textarea nicht gefunden"}).eq("id", pid).execute()
            log.warning("  ✗ Fehlgeschlagen")

        time.sleep(2)

    return sent_count


def main():
    log.info("=== Send Worker gestartet (Interval: %ds) ===", INTERVAL)
    db = get_db()

    pw = browser = ctx = page = None
    session_errors = 0

    while True:
        try:
            # (Re)connect if needed
            if page is None:
                pw, browser, ctx, page = get_browser_page()
                session_errors = 0

            sent = drain_queue(page, db)
            if sent:
                log.info("Queue geleert: %d Nachricht(en) gesendet", sent)

        except KeyboardInterrupt:
            log.info("Worker gestoppt.")
            break
        except Exception as e:
            log.error("Fehler: %s", e)
            session_errors += 1
            # After 3 errors, force re-login
            if session_errors >= 3:
                log.info("Zu viele Fehler — Browser neu starten...")
                try:
                    if browser: browser.close()
                    if pw: pw.stop()
                except Exception:
                    pass
                pw = browser = ctx = page = None
                session_errors = 0
                time.sleep(10)

        time.sleep(INTERVAL)

    try:
        if browser: browser.close()
        if pw: pw.stop()
    except Exception:
        pass


if __name__ == "__main__":
    main()
