"""
DripifySender — opens the conversation in a headless browser and sends a reply.
Reuses the stored session so no login is needed on every send.
"""
from __future__ import annotations
import json
import logging
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

log = logging.getLogger(__name__)

SESSION_FILE = Path("dripify_session.json")
BASE_URL     = "https://app.dripify.com"

# Multiple selectors for the reply textarea — Dripify may change their DOM
_TEXTAREA_SELS = [
    "div.chat-footer textarea",
    "textarea.message-input",
    "textarea[placeholder]",
    ".chat-input textarea",
    "[class*='footer'] textarea",
    "[class*='input'] textarea",
    "textarea",
]
_SEND_BTN_SELS = [
    "button.send-btn",
    "button[class*='send']",
    "[class*='footer'] button:last-child",
    "[class*='chat'] button[type='submit']",
    "button[aria-label*='send' i]",
    "button[aria-label*='senden' i]",
]

# Selectors for profile fields in the right panel
_PROFILE_SELS = {
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
    "linkedin_url": [
        ".messages__lead-card a[href*='linkedin.com']",
        ".lead-card a[href*='linkedin.com']",
        "[class*='lead'] a[href*='linkedin.com/in/']",
    ],
    "email": [
        ".messages__lead-card a[href^='mailto:']",
        ".lead-card a[href^='mailto:']",
        "[class*='lead'] a[href^='mailto:']",
        "[class*='email'] a[href^='mailto:']",
    ],
    "connections_count": [
        ".messages__lead-card [class*='connection']",
        ".lead-card [class*='connection']",
        "[class*='lead'] [class*='connection']",
        "[class*='lead'] [class*='follower']",
    ],
}


def _load_session() -> dict:
    if SESSION_FILE.exists():
        try:
            return json.loads(SESSION_FILE.read_text())
        except Exception:
            pass
    return {}


def send_message(dripify_contact_id: str, text: str) -> dict:
    """
    Open the Dripify conversation and send a message.
    Returns {"ok": True} or {"ok": False, "error": "..."}.
    """
    href = f"/inbox/{dripify_contact_id}"
    url  = f"{BASE_URL}{href}"

    pw = sync_playwright().start()
    try:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        storage = _load_session()
        ctx = browser.new_context(
            storage_state=storage if storage else None,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
        )
        page = ctx.new_page()

        # Navigate to conversation
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        time.sleep(3)

        # Check if we got redirected to login
        if any(x in page.url for x in ["sign-in", "login", "auth"]):
            return {"ok": False, "error": "Session abgelaufen — bitte einmal manuell Dripify-Sync starten"}

        # Find reply textarea
        textarea = None
        for sel in _TEXTAREA_SELS:
            try:
                el = page.wait_for_selector(sel, timeout=4000)
                if el and el.is_visible():
                    textarea = el
                    log.info("Found textarea via: %s", sel)
                    break
            except PWTimeout:
                continue

        if not textarea:
            page.screenshot(path="send_error.png")
            return {"ok": False, "error": "Texteingabe nicht gefunden — Screenshot: send_error.png"}

        # Click, clear, type
        textarea.click()
        time.sleep(0.3)
        textarea.fill(text)
        time.sleep(0.5)

        # Find and click send button
        sent = False
        for sel in _SEND_BTN_SELS:
            try:
                btn = page.query_selector(sel)
                if btn and btn.is_visible() and btn.is_enabled():
                    btn.click()
                    sent = True
                    log.info("Sent via button: %s", sel)
                    break
            except Exception:
                continue

        # Fallback: Enter key
        if not sent:
            textarea.press("Enter")
            log.info("Sent via Enter key fallback")

        time.sleep(1.5)
        log.info("Message sent to %s", dripify_contact_id)
        return {"ok": True}

    except Exception as e:
        log.exception("Send failed: %s", e)
        return {"ok": False, "error": str(e)}
    finally:
        try:
            browser.close()
            pw.stop()
        except Exception:
            pass


def scrape_profile(dripify_contact_id: str) -> dict:
    """
    Open the Dripify conversation and scrape full profile info from the right panel.
    Returns {"avatar_url", "title", "company_name", "location", "linkedin_url"}.
    """
    href = f"/inbox/{dripify_contact_id}"
    url  = f"{BASE_URL}{href}"

    pw = sync_playwright().start()
    result: dict = {}
    try:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        storage = _load_session()
        ctx = browser.new_context(
            storage_state=storage if storage else None,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
        )
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        time.sleep(3)

        if any(x in page.url for x in ["sign-in", "login", "auth"]):
            return {}

        # Avatar
        for sel in [".messages__lead-card .avatar img", ".messages__lead .avatar img",
                    "[class*='lead'] .avatar img", "[class*='lead'] img"]:
            try:
                el = page.query_selector(sel)
                if el:
                    src = el.get_attribute("src") or ""
                    if "licdn.com" in src or "media.licdn" in src:
                        result["avatar_url"] = src
                        break
            except Exception:
                pass

        # Text / href fields
        for field, sels in _PROFILE_SELS.items():
            for sel in sels:
                try:
                    el = page.query_selector(sel)
                    if el:
                        if field in ("linkedin_url", "email"):
                            href = el.get_attribute("href") or ""
                            val = href.replace("mailto:", "").strip() if field == "email" else href
                        else:
                            val = (el.inner_text() or "").strip()
                        if val:
                            result[field] = val
                            break
                except Exception:
                    continue

        log.info("Scraped profile for %s: %s", dripify_contact_id, list(result.keys()))
        return result

    except Exception as e:
        log.exception("Profile scrape failed: %s", e)
        return {}
    finally:
        try:
            browser.close()
            pw.stop()
        except Exception:
            pass
