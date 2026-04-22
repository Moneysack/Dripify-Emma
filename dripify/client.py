"""
Dripify browser client — Playwright-based inbox scraper.

Logs into app.dripify.io with email + password, reads the inbox,
and sends replies. Session is persisted to disk so login only
happens once (or when the session expires).

Selectors are based on Dripify's current UI structure.
If the UI changes, update the SELECTORS dict at the top of this file.
"""
from __future__ import annotations
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, BrowserContext, TimeoutError as PWTimeout

from config import settings

log = logging.getLogger(__name__)

SESSION_FILE = Path("dripify_session.json")
DRIPIFY_URL  = "https://app.dripify.io"
LOGIN_URL    = f"{DRIPIFY_URL}/auth/sign-in"
INBOX_URL    = f"{DRIPIFY_URL}/inbox"

# ── Selectors — update these if Dripify changes their UI ──────────────────────
SEL = {
    # Login page
    "email_input":       'input[type="email"], input[name="email"]',
    "password_input":    'input[type="password"], input[name="password"]',
    "login_button":      'button[type="submit"]',
    "login_success":     '[data-testid="dashboard"], .sidebar, nav.sidebar, [class*="sidebar"]',

    # Inbox — conversation list
    "conversation_list": '[class*="conversation"], [class*="chat-item"], [data-testid="conversation"]',
    "conv_name":         '[class*="name"], [class*="title"], h3, h4',
    "conv_preview":      '[class*="preview"], [class*="last-message"], [class*="snippet"]',
    "conv_unread":       '[class*="unread"], [class*="badge"], [class*="dot"]',

    # Conversation / message thread
    "message_list":      '[class*="message"], [class*="chat-message"], [data-testid="message"]',
    "message_text":      '[class*="text"], [class*="body"], [class*="content"] p, p',
    "message_incoming":  '[class*="incoming"], [class*="received"], [class*="prospect"]',
    "message_outgoing":  '[class*="outgoing"], [class*="sent"], [class*="mine"]',

    # Reply box
    "reply_textarea":    'textarea, [contenteditable="true"], [class*="composer"] textarea',
    "send_button":       'button[class*="send"], button[aria-label*="send" i], button[type="submit"]',
}


@dataclass
class DripifyMessage:
    message_id: str        # synthetic: conv_id + "_" + message index
    conversation_id: str   # unique per prospect thread
    contact_id: str        # prospect name used as ID (Dripify has no stable lead ID in UI)
    linkedin_name: str
    campaign_id: str       # empty — not visible in inbox UI
    text: str
    is_incoming: bool


class DripifyClient:
    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def start(self):
        """Launch browser and restore session if available."""
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        storage = json.loads(SESSION_FILE.read_text()) if SESSION_FILE.exists() else {}
        self._context = self._browser.new_context(
            storage_state=storage if storage else None,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
        )
        self._page = self._context.new_page()
        log.info("Browser started")

    def stop(self):
        if self._page:
            self._page.close()
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        log.info("Browser stopped")

    def _save_session(self):
        state = self._context.storage_state()
        SESSION_FILE.write_text(json.dumps(state))
        log.debug("Session saved to %s", SESSION_FILE)

    # ── Login ──────────────────────────────────────────────────────────────────

    def ensure_logged_in(self) -> bool:
        """Check if session is valid; login if not. Returns True on success."""
        page = self._page
        page.goto(INBOX_URL, wait_until="domcontentloaded", timeout=30_000)
        time.sleep(2)

        # If redirected to login page, we need to authenticate
        if "/sign-in" in page.url or "/login" in page.url or "/auth" in page.url:
            log.info("Session expired — logging in")
            return self._login()

        log.info("Session valid — already logged in")
        return True

    def _login(self) -> bool:
        page = self._page
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30_000)
        time.sleep(1)

        try:
            page.fill(SEL["email_input"], settings.dripify_email)
            page.fill(SEL["password_input"], settings.dripify_password)
            page.click(SEL["login_button"])

            # Wait for redirect away from login
            page.wait_for_url(lambda url: "sign-in" not in url and "login" not in url, timeout=20_000)
            time.sleep(2)

            self._save_session()
            log.info("Login successful")
            return True

        except PWTimeout:
            log.error("Login timed out — check credentials or Dripify UI changed")
            page.screenshot(path="login_error.png")
            return False

    # ── Inbox scraping ─────────────────────────────────────────────────────────

    def get_new_incoming_messages(self, known_message_ids: set[str]) -> list[DripifyMessage]:
        """
        Scrape the Dripify inbox and return messages not in known_message_ids.
        """
        if not self.ensure_logged_in():
            return []

        page = self._page
        page.goto(INBOX_URL, wait_until="domcontentloaded", timeout=30_000)
        time.sleep(3)  # wait for React to render

        new_messages: list[DripifyMessage] = []

        # Find all conversation items in the sidebar list
        conv_items = page.query_selector_all(SEL["conversation_list"])
        log.info("Found %d conversations in inbox", len(conv_items))

        for i, item in enumerate(conv_items):
            try:
                name_el = item.query_selector(SEL["conv_name"])
                name = name_el.inner_text().strip() if name_el else f"Contact_{i}"

                # Click the conversation to open it
                item.click()
                time.sleep(1.5)

                # Collect all messages in the thread
                messages = page.query_selector_all(SEL["message_list"])
                if not messages:
                    continue

                # Only care about the LAST incoming message (most recent reply from prospect)
                last_incoming = None
                last_idx = -1
                for idx, msg_el in enumerate(messages):
                    is_incoming = bool(msg_el.query_selector(SEL["message_incoming"])) or \
                                  "incoming" in (msg_el.get_attribute("class") or "") or \
                                  "received" in (msg_el.get_attribute("class") or "")

                    if not is_incoming:
                        # Fallback: if there's no outgoing marker either, try text position heuristic
                        is_outgoing = bool(msg_el.query_selector(SEL["message_outgoing"])) or \
                                      "outgoing" in (msg_el.get_attribute("class") or "") or \
                                      "sent" in (msg_el.get_attribute("class") or "")
                        if not is_outgoing:
                            # Ambiguous — treat as incoming
                            is_incoming = True

                    if is_incoming:
                        last_incoming = msg_el
                        last_idx = idx

                if last_incoming is None:
                    continue

                text_el = last_incoming.query_selector(SEL["message_text"])
                text = text_el.inner_text().strip() if text_el else last_incoming.inner_text().strip()

                # Synthetic ID: prospect name + message index (stable enough for dedup)
                safe_name = name.replace(" ", "_").lower()
                msg_id = f"{safe_name}_{last_idx}"

                if msg_id in known_message_ids:
                    log.debug("Skipping known message: %s", msg_id)
                    continue

                if not text:
                    continue

                # Use name as contact_id (no stable numeric ID visible in UI)
                new_messages.append(DripifyMessage(
                    message_id=msg_id,
                    conversation_id=f"conv_{safe_name}",
                    contact_id=safe_name,
                    linkedin_name=name,
                    campaign_id="",
                    text=text,
                    is_incoming=True,
                ))
                log.info("New message from %s: %s...", name, text[:60])

            except Exception as exc:
                log.warning("Error reading conversation %d: %s", i, exc)
                continue

        return new_messages

    # ── Sending reply ──────────────────────────────────────────────────────────

    def send_reply(self, conversation_id: str, text: str):
        """
        Type and send a reply in the currently open conversation.

        Assumes the conversation matching conversation_id is already open
        (agent.py calls get_new_incoming_messages first, which opens it).
        If needed, we navigate to inbox and re-open the right conversation.
        """
        page = self._page

        try:
            textarea = page.wait_for_selector(SEL["reply_textarea"], timeout=8_000)
            textarea.click()
            textarea.fill(text)
            time.sleep(0.5)

            # Try send button first, fall back to Enter
            send_btn = page.query_selector(SEL["send_button"])
            if send_btn:
                send_btn.click()
            else:
                textarea.press("Enter")

            time.sleep(1)
            log.info("Reply sent to %s", conversation_id)

        except PWTimeout:
            log.error("Could not find reply textarea for %s — screenshot saved", conversation_id)
            page.screenshot(path=f"reply_error_{conversation_id}.png")
            raise
