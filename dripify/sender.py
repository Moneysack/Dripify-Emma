"""
DripifySender — opens the conversation in a headless browser and sends a reply.
Profile scraping uses page.evaluate() with the real Dripify DOM structure.
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

# Keep for backward compat (sync.py imports this)
_PROFILE_SELS = {}

# JS extractor — uses the real Dripify panel DOM (inspected from profile_panel.html)
_PROFILE_JS = """() => {
    const r = {};
    try {
        // Avatar
        const img = document.querySelector('.avatar__userpic');
        if (img) r.avatar_url = img.getAttribute('src') || '';

        // LinkedIn URL
        const liLink = document.querySelector('.lead-info__li-logo');
        if (liLink) r.linkedin_url = liLink.getAttribute('href') || '';

        // Occupation line: "CEO @ iinovis"
        const occ = document.querySelector('.lead-info__occupation');
        if (occ) {
            const t = occ.innerText.trim().replace(/\\s+/g, ' ');
            if (t.includes(' @ ')) {
                const parts = t.split(' @ ');
                r.title        = parts[0].trim();
                r.company_name = parts.slice(1).join(' @ ').trim();
            } else {
                r.title = t;
            }
        }

        // Connections count ("1250 connections")
        const bodyS = document.querySelector('.body_S');
        if (bodyS) {
            for (const d of bodyS.querySelectorAll('div')) {
                const t = d.innerText.trim();
                if (t.toLowerCase().includes('connection')) {
                    r.connections_count = t.replace(/connections?/i, '').trim();
                    break;
                }
            }
        }

        // Structured li items: Company / Position / City / Country
        for (const li of document.querySelectorAll('li.lead-info__item')) {
            const cap = li.querySelector('.lead-info__item-caption');
            const val = li.querySelector('div:not(.lead-info__item-caption)');
            if (!cap || !val) continue;
            const k = cap.innerText.trim().toLowerCase();
            const v = val.innerText.trim();
            if      (k === 'company')  r.company_name = r.company_name || v;
            else if (k === 'position') r.title        = r.title        || v;
            else if (k === 'city')     r.location     = v;
            else if (k === 'country')  r.country      = v;
        }

        // Combine city + country into location
        if (!r.location && r.country)  r.location = r.country;
        else if (r.location && r.country && !r.location.includes(r.country))
            r.location = r.location + ', ' + r.country;

        // Email from mailto link
        const mailto = document.querySelector('a[href^="mailto:"]');
        if (mailto) r.email = (mailto.getAttribute('href') || '').replace('mailto:', '').trim();

    } catch(e) { r._error = String(e); }
    return r;
}"""


def _load_session() -> dict:
    if SESSION_FILE.exists():
        try:
            return json.loads(SESSION_FILE.read_text())
        except Exception:
            pass
    return {}


def _make_context(pw):
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
    return browser, ctx


def send_message(dripify_contact_id: str, text: str) -> dict:
    """Open the Dripify conversation and send a message."""
    url = f"{BASE_URL}/inbox/{dripify_contact_id}"
    pw = sync_playwright().start()
    try:
        browser, ctx = _make_context(pw)
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        time.sleep(3)

        if any(x in page.url for x in ["sign-in", "login", "auth"]):
            return {"ok": False, "error": "Session abgelaufen — bitte einmal manuell Dripify-Sync starten"}

        # Find textarea
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

        textarea.click()
        time.sleep(0.3)
        textarea.fill(text)
        time.sleep(0.5)

        # Click send button
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
    """Open the Dripify conversation and scrape full profile from the right panel."""
    url = f"{BASE_URL}/inbox/{dripify_contact_id}"
    pw = sync_playwright().start()
    try:
        browser, ctx = _make_context(pw)
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        time.sleep(4)

        if any(x in page.url for x in ["sign-in", "login", "auth"]):
            return {}

        result = page.evaluate(_PROFILE_JS) or {}
        result.pop("_error", None)
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


def scrape_profile_on_page(page) -> dict:
    """Scrape profile from an already-open conversation page (used by sync)."""
    try:
        result = page.evaluate(_PROFILE_JS) or {}
        result.pop("_error", None)
        return result
    except Exception as e:
        log.debug("Profile evaluate error: %s", e)
        return {}
