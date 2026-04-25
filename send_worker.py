"""
Send Worker — lokal starten: python send_worker.py
Prüft alle 5 Sekunden die pending_sends Queue und sendet via Dripify.
Login passiert einmalig beim Start, bei Session-Ablauf automatisch neu.
"""
from __future__ import annotations
import json, logging, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("worker")

from config import settings
from database.client import get_db

BASE     = "https://app.dripify.com"
INTERVAL = 5   # Sekunden zwischen Queue-Checks
SESSION  = Path("dripify_session.json")

TEXTAREA_SELS = ["textarea[placeholder]", "div.chat-footer textarea",
                 "textarea.message-input", ".chat-input textarea", "textarea"]
SEND_SELS     = ["button[class*='send']", "button.send-btn",
                 "[class*='footer'] button:last-child", "button[aria-label*='send' i]"]


class Worker:
    def __init__(self):
        self.pw = self.browser = self.ctx = self.page = None
        self.db = get_db()

    # ── Browser lifecycle ────────────────────────────────────────────────────
    def start_browser(self):
        from playwright.sync_api import sync_playwright
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        self.ctx = self.browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
        )
        self.page = self.ctx.new_page()

    def stop_browser(self):
        for obj in [self.browser, self.pw]:
            try:
                if obj: obj.close() if hasattr(obj, "close") else obj.stop()
            except Exception:
                pass
        self.pw = self.browser = self.ctx = self.page = None

    def login(self) -> bool:
        page = self.page
        log.info("Login als %s ...", settings.dripify_email)
        page.goto(BASE, wait_until="domcontentloaded", timeout=30_000)
        time.sleep(3)

        for sel in ["#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
                    'button:has-text("Allow all")', 'button:has-text("Accept All")']:
            try:
                btn = page.wait_for_selector(sel, timeout=3000)
                if btn and btn.is_visible(): btn.click(); time.sleep(2); break
            except Exception:
                pass

        page.fill('input[type="email"]', settings.dripify_email)
        page.fill('input[type="password"]', settings.dripify_password)
        page.click('button[type="submit"]')
        try:
            page.wait_for_function(
                "() => window.location.href.includes('dripify.com') && "
                "      !window.location.href.includes('sign-in')",
                timeout=30_000,
            )
        except Exception:
            log.error("Login fehlgeschlagen. URL: %s", page.url)
            return False

        time.sleep(3)
        try:
            SESSION.write_text(json.dumps(self.ctx.storage_state()))
        except Exception:
            pass
        log.info("Login OK: %s", page.url)
        return True

    def is_logged_in(self) -> bool:
        return self.page is not None and not any(
            x in (self.page.url or "") for x in ["sign-in", "login", "app.dripify.com/"]
        )

    # ── Send one message ─────────────────────────────────────────────────────
    def send_one(self, did: str, text: str) -> bool:
        page = self.page
        page.goto(f"{BASE}/inbox/{did}", wait_until="domcontentloaded", timeout=30_000)
        time.sleep(4)

        # Session expired?
        if any(x in page.url for x in ["sign-in", "login"]):
            log.warning("Session abgelaufen während Send — re-login...")
            if not self.login():
                return False
            page.goto(f"{BASE}/inbox/{did}", wait_until="domcontentloaded", timeout=30_000)
            time.sleep(4)

        # Find textarea
        ta = None
        for sel in TEXTAREA_SELS:
            try:
                el = page.wait_for_selector(sel, timeout=5000)
                if el and el.is_visible():
                    ta = el; break
            except Exception:
                continue

        if not ta:
            log.error("Textarea nicht gefunden für %s", did[:20])
            return False

        ta.click(); time.sleep(0.3)
        ta.fill(text); time.sleep(0.5)

        sent = False
        for sel in SEND_SELS:
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

    # ── Drain queue ──────────────────────────────────────────────────────────
    def drain(self):
        pending = self.db.table("pending_sends").select("*") \
            .eq("status", "pending").execute().data
        if not pending:
            return

        log.info("Queue: %d Nachricht(en)", len(pending))
        for p in pending:
            did  = p.get("dripify_contact_id", "")
            text = p.get("text", "")
            pid  = p["id"]
            if not did or not text:
                continue

            log.info("  -> %s", repr(text[:55]))
            ok = self.send_one(did, text)

            if ok:
                self.db.table("pending_sends") \
                    .update({"status": "sent", "sent_at": "now()"}) \
                    .eq("id", pid).execute()
                try:
                    self.db.table("messages").update({"sent_to_dripify": True}) \
                        .eq("contact_id", p["contact_id"]) \
                        .eq("text", text).eq("direction", "outgoing").execute()
                except Exception:
                    pass
                log.info("  ✓ Gesendet")
            else:
                self.db.table("pending_sends") \
                    .update({"status": "failed", "error_msg": "Textarea nicht gefunden"}) \
                    .eq("id", pid).execute()
                log.warning("  ✗ Fehler")

            time.sleep(1)

    # ── Main loop ────────────────────────────────────────────────────────────
    def run(self):
        log.info("=== Send Worker gestartet (alle %ds) ===", INTERVAL)
        errors = 0

        self.start_browser()
        if not self.login():
            log.error("Login beim Start fehlgeschlagen. Beende.")
            self.stop_browser()
            return

        while True:
            try:
                self.drain()
                errors = 0
            except KeyboardInterrupt:
                break
            except Exception as e:
                errors += 1
                log.error("Fehler #%d: %s", errors, e)
                if errors >= 5:
                    log.info("Zu viele Fehler — Browser neu starten...")
                    self.stop_browser()
                    time.sleep(5)
                    self.start_browser()
                    self.login()
                    errors = 0

            time.sleep(INTERVAL)

        log.info("Worker gestoppt.")
        self.stop_browser()


if __name__ == "__main__":
    Worker().run()
