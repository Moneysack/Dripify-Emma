"""
Dripify Inbox Sync — reads all conversations from Dripify and stores them in Supabase.
No auto-reply. Import only.
"""
from __future__ import annotations
import logging
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from database.client import get_db

log = logging.getLogger(__name__)

SESSION_FILE = Path("dripify_session.json")
BASE_URL     = "https://app.dripify.com"
INBOX_URL    = f"{BASE_URL}/inbox"


class DripifySync:
    def __init__(self, email: str, password: str):
        self.email    = email
        self.password = password
        self._pw      = None
        self._browser = None
        self._context = None
        self._page    = None

    def start(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        storage = {}
        if SESSION_FILE.exists():
            try:
                storage = json.loads(SESSION_FILE.read_text())
            except Exception:
                storage = {}

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

    def stop(self):
        for obj in [self._page, self._context, self._browser, self._pw]:
            try:
                if obj:
                    obj.close() if hasattr(obj, "close") else obj.stop()
            except Exception:
                pass

    def _save_session(self):
        try:
            SESSION_FILE.write_text(json.dumps(self._context.storage_state()))
        except Exception:
            pass

    # ── Cookie consent ─────────────────────────────────────────────────────────
    def _accept_cookies(self):
        page = self._page
        for sel in [
            "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
            'button:has-text("Allow all")',
            'button:has-text("Accept All")',
            'button:has-text("Accept all")',
        ]:
            try:
                btn = page.wait_for_selector(sel, timeout=4000)
                if btn and btn.is_visible():
                    btn.click()
                    log.info("Cookie consent accepted via: %s", sel)
                    time.sleep(2)
                    return
            except PWTimeout:
                continue

    # ── Login ──────────────────────────────────────────────────────────────────
    def _ensure_logged_in(self) -> bool:
        page = self._page

        # Try inbox directly first (session may still be valid)
        page.goto(INBOX_URL, wait_until="domcontentloaded", timeout=30_000)
        self._accept_cookies()
        time.sleep(2)

        # Check if redirected to login
        if any(x in page.url for x in ["sign-in", "login", "auth"]):
            return self._login()

        # Also check if we're on the root (not logged in yet)
        if page.url.rstrip("/") == BASE_URL:
            return self._login()

        log.info("Session valid, already logged in: %s", page.url)
        return True

    def _login(self) -> bool:
        page = self._page
        log.info("Logging into Dripify as %s", self.email)

        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30_000)
        time.sleep(3)
        self._accept_cookies()
        time.sleep(1)

        # Wait for email field
        try:
            page.wait_for_selector('input[type="email"]', timeout=10_000)
        except PWTimeout:
            page.screenshot(path="login_error.png")
            log.error("Email input not found after 10s. Screenshot: login_error.png")
            return False

        # Fill credentials
        page.fill('input[type="email"]', self.email)
        page.fill('input[type="password"]', self.password)
        page.click('button[type="submit"]')
        log.info("Submitted login form")

        # Wait for redirect away from root/login
        try:
            page.wait_for_function(
                "() => !window.location.href.endsWith('app.dripify.com/') && "
                "       !window.location.href.includes('sign-in') && "
                "       window.location.href.includes('dripify.com')",
                timeout=30_000,
            )
        except PWTimeout:
            page.screenshot(path="login_error.png")
            log.error("Login redirect timeout. URL: %s — screenshot: login_error.png", page.url)
            return False

        time.sleep(3)
        self._save_session()
        log.info("Login successful: %s", page.url)
        return True

    # ── Load all conversations ─────────────────────────────────────────────────
    def _get_conversation_links(self) -> list[dict]:
        """Return list of {name, conv_id, href} for all visible conversations."""
        page = self._page

        page.goto(INBOX_URL, wait_until="networkidle", timeout=30_000)
        time.sleep(4)
        log.info("Inbox loaded: %s", page.url)

        # Click "Load more" until all conversations are visible
        for _ in range(20):  # max 20 pages
            try:
                # Re-query fresh each iteration to avoid stale element
                btns = page.query_selector_all('button.tertiary-btn')
                load_btn = None
                for b in btns:
                    try:
                        if "load more" in (b.inner_text() or "").lower() and b.is_visible():
                            load_btn = b
                            break
                    except Exception:
                        continue
                if not load_btn:
                    break
                load_btn.click()
                time.sleep(2)
            except Exception:
                break

        items = page.query_selector_all("a.chats-list__item")
        log.info("Found %d conversation items", len(items))

        convs = []
        for item in items:
            try:
                href = item.get_attribute("href") or ""
                conv_id = href.split("/inbox/")[-1] if "/inbox/" in href else ""
                name_el = item.query_selector("div.chat-item__name")
                name = name_el.inner_text().strip() if name_el else conv_id[:30]
                if not conv_id:
                    continue
                # Grab LinkedIn avatar URL
                avatar_url = ""
                try:
                    img_el = item.query_selector(".avatar img, .chat-item__avatar img, img.avatar__userpic")
                    if img_el:
                        avatar_url = img_el.get_attribute("src") or ""
                except Exception:
                    pass
                convs.append({"name": name, "conv_id": conv_id, "href": href, "avatar_url": avatar_url})
            except Exception as e:
                log.debug("Error reading item: %s", e)

        return convs

    # ── Extract messages from open conversation ────────────────────────────────
    def _extract_messages(self) -> list[dict]:
        """Extract all messages from the currently displayed conversation."""
        page = self._page
        time.sleep(2)

        # Scroll to top to load all messages
        try:
            msg_container = page.query_selector(".messages__chat, [class*='messages__chat']")
            if msg_container:
                msg_container.evaluate("el => el.scrollTop = 0")
                time.sleep(1)
        except Exception:
            pass

        msg_els = page.query_selector_all("div.msg")
        if not msg_els:
            log.warning("No div.msg elements found in conversation")
            return []

        messages = []
        for el in msg_els:
            try:
                cls = el.get_attribute("class") or ""
                text = el.inner_text().strip()
                if not text or len(text) < 1:
                    continue
                # "msg--my" means outgoing (sent by us)
                direction = "outgoing" if "msg--my" in cls else "incoming"
                messages.append({"direction": direction, "text": text})
            except Exception:
                continue

        log.debug("Extracted %d messages", len(messages))
        return messages

    # ── Main sync ──────────────────────────────────────────────────────────────
    def sync_all(self) -> dict:
        db = get_db()
        summary = {"contacts_new": 0, "contacts_existing": 0, "messages_new": 0}

        if not self._ensure_logged_in():
            return {"error": "Login failed — check login_error.png"}

        convs = self._get_conversation_links()
        if not convs:
            page = self._page
            page.screenshot(path="inbox_debug.png")
            html = page.evaluate("() => document.body.innerHTML.substring(0, 5000)")
            Path("inbox_debug.html").write_text(html, encoding="utf-8")
            return {"error": "No conversations found — check inbox_debug.png and inbox_debug.html"}

        for conv in convs:
            name    = conv["name"]
            conv_id = conv["conv_id"]
            log.info("Syncing: %s (id=%s)", name, conv_id[:20])

            try:
                # Navigate to conversation
                page = self._page
                page.goto(f"{BASE_URL}{conv['href']}", wait_until="domcontentloaded", timeout=30_000)
                time.sleep(2)

                # Scrape full profile from the right panel
                avatar_url   = conv.get("avatar_url", "")
                title        = ""
                company_name = ""
                location     = ""
                linkedin_url = ""
                try:
                    from dripify.sender import _PROFILE_SELS
                    # Avatar
                    for sel in [".messages__lead-card .avatar img", ".messages__lead .avatar img",
                                ".messages__lead img.avatar__userpic", ".lead-card .avatar img",
                                "[class*='lead'] .avatar img", "[class*='lead'] img"]:
                        img_el = page.query_selector(sel)
                        if img_el:
                            src = img_el.get_attribute("src") or ""
                            if src and "licdn.com" in src:
                                avatar_url = src
                                break
                    # Text profile fields
                    for field, sels in _PROFILE_SELS.items():
                        for sel in sels:
                            try:
                                el = page.query_selector(sel)
                                if el:
                                    val = el.get_attribute("href") if field == "linkedin_url" else (el.inner_text() or "").strip()
                                    if val:
                                        if field == "title":        title = val
                                        elif field == "company_name": company_name = val
                                        elif field == "location":    location = val
                                        elif field == "linkedin_url": linkedin_url = val
                                        break
                            except Exception:
                                continue
                except Exception:
                    pass

                # Upsert contact using conv_id as stable identifier
                existing = (
                    db.table("contacts")
                    .select("id")
                    .eq("dripify_contact_id", conv_id)
                    .execute()
                    .data
                )
                if existing:
                    contact_id = existing[0]["id"]
                    summary["contacts_existing"] += 1
                    update_data = {"linkedin_name": name}
                    if avatar_url:    update_data["avatar_url"]   = avatar_url
                    if title:         update_data["title"]         = title
                    if company_name:  update_data["company_name"]  = company_name
                    if location:      update_data["location"]      = location
                    if linkedin_url:  update_data["linkedin_url"]  = linkedin_url
                    try:
                        db.table("contacts").update(update_data).eq("id", contact_id).execute()
                    except Exception:
                        pass
                else:
                    row = (
                        db.table("contacts")
                        .insert({
                            "dripify_contact_id": conv_id,
                            "linkedin_name":  name,
                            "campaign_id":    "",
                            "avatar_url":     avatar_url,
                            "title":          title,
                            "company_name":   company_name,
                            "location":       location,
                            "linkedin_url":   linkedin_url,
                        })
                        .execute()
                        .data[0]
                    )
                    contact_id = row["id"]
                    db.table("emma_state").insert({"contact_id": contact_id}).execute()
                    db.table("conversations").insert({"contact_id": contact_id}).execute()
                    summary["contacts_new"] += 1

                # Extract messages
                msgs = self._extract_messages()
                existing_msgs = (
                    db.table("messages")
                    .select("text,direction")
                    .eq("contact_id", contact_id)
                    .execute()
                    .data
                )
                existing_set = {(m["direction"], m["text"][:80]) for m in existing_msgs}

                new_msgs = [
                    {
                        "contact_id": contact_id,
                        "direction":  m["direction"],
                        "text":       m["text"],
                        "dripify_msg_id": conv_id,
                    }
                    for m in msgs
                    if (m["direction"], m["text"][:80]) not in existing_set
                ]
                if new_msgs:
                    db.table("messages").insert(new_msgs).execute()
                    summary["messages_new"] += len(new_msgs)
                    log.info("  Stored %d new messages for %s", len(new_msgs), name)

            except Exception as e:
                log.exception("Error syncing '%s': %s", name, e)

        log.info("Sync done: %s", summary)
        return summary
