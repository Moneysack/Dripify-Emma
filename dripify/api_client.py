"""
DripifyApiClient — sends messages via Dripify's internal REST API.
Login is done once via Playwright to capture the Bearer token.
All subsequent calls use httpx (fast, no browser).
"""
from __future__ import annotations
import json
import logging
import time
from pathlib import Path

import httpx

log = logging.getLogger(__name__)

BASE = "https://app.dripify.com"
TOKEN_FILE = Path("dripify_token.json")
TOKEN_TTL = 3000  # re-login after 50 minutes (Firebase tokens live 60 min)


class DripifyApiClient:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self._token: str | None = None
        self._token_at: float = 0
        self._conv_cache: dict[str, str] = {}  # short_id → full_id

    # ── Auth ────────────────────────────────────────────────────────────────
    def _load_token(self) -> bool:
        if TOKEN_FILE.exists():
            try:
                d = json.loads(TOKEN_FILE.read_text())
                if time.time() - d.get("at", 0) < TOKEN_TTL:
                    self._token = d["token"]
                    self._token_at = d["at"]
                    return True
            except Exception:
                pass
        return False

    def _save_token(self):
        try:
            TOKEN_FILE.write_text(json.dumps({"token": self._token, "at": self._token_at}))
        except Exception:
            pass

    def _login_playwright(self) -> bool:
        """Launch a headless browser, log into Dripify, capture Bearer token."""
        from playwright.sync_api import sync_playwright
        captured = []

        pw = sync_playwright().start()
        try:
            browser = pw.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            )
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1440, "height": 900},
            )
            page = ctx.new_page()

            def on_request(req):
                if "app.dripify.com/api" in req.url and not captured:
                    h = dict(req.headers)
                    auth = h.get("authorization") or h.get("Authorization") or ""
                    if auth.startswith("Bearer "):
                        captured.append(auth[7:])

            page.on("request", on_request)

            log.info("Playwright login as %s …", self.email)
            page.goto(BASE, wait_until="domcontentloaded", timeout=30_000)
            time.sleep(3)

            for sel in [
                "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
                'button:has-text("Allow all")',
                'button:has-text("Accept All")',
            ]:
                try:
                    btn = page.wait_for_selector(sel, timeout=3000)
                    if btn and btn.is_visible():
                        btn.click()
                        time.sleep(2)
                        break
                except Exception:
                    pass

            page.fill('input[type="email"]', self.email)
            page.fill('input[type="password"]', self.password)
            page.click('button[type="submit"]')
            page.wait_for_function(
                "() => !window.location.href.endsWith('app.dripify.com/') && "
                "      !window.location.href.includes('sign-in') && "
                "      window.location.href.includes('dripify.com')",
                timeout=30_000,
            )
            time.sleep(3)

            # Trigger a real API call to capture the token
            page.goto(f"{BASE}/inbox", wait_until="networkidle", timeout=45_000)
            time.sleep(2)

            browser.close()
        finally:
            pw.stop()

        if captured:
            self._token = captured[0]
            self._token_at = time.time()
            self._save_token()
            log.info("Token captured OK")
            return True
        log.error("No Bearer token captured from login")
        return False

    def _ensure_token(self) -> bool:
        if self._token and time.time() - self._token_at < TOKEN_TTL:
            return True
        if self._load_token():
            return True
        return self._login_playwright()

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
            ),
            "Origin": BASE,
            "Referer": f"{BASE}/inbox",
        }

    # ── Conversation ID lookup ───────────────────────────────────────────────
    def _fetch_full_id(self, short_id: str) -> str | None:
        """Fetch all conversations and find the one whose ID starts with short_id."""
        page_num = 0
        while page_num < 10:
            url = f"{BASE}/api/messaging/conversations?archived=false&size=50&page={page_num}"
            r = httpx.get(url, headers=self._headers(), timeout=30)
            if r.status_code == 401:
                return None  # token expired
            data = r.json()
            items = data.get("content", [])
            for item in items:
                lc = item.get("linkedinConversation", {})
                full_id = lc.get("id", "")
                if full_id.startswith(short_id):
                    return full_id
            if data.get("last", True):
                break
            page_num += 1
        return None

    def get_full_conversation_id(self, short_id: str) -> str | None:
        if short_id in self._conv_cache:
            return self._conv_cache[short_id]
        full_id = self._fetch_full_id(short_id)
        if full_id:
            self._conv_cache[short_id] = full_id
        return full_id

    # ── Lead enrichment ─────────────────────────────────────────────────────
    def get_lead_data(self, lead_in_user_id: int) -> dict:
        """Fetch full lead profile from /api/leads/{id}."""
        r = httpx.get(f"{BASE}/api/leads/{lead_in_user_id}", headers=self._headers(), timeout=30)
        if r.status_code != 200:
            return {}
        d = r.json()
        camp = {}
        for c in d.get("leadInCampaigns", []):
            # prefer the active/most recent campaign
            if not camp or c["campaign"].get("status") == "ACTIVE":
                camp = c
        time_in_role = ""
        tir = d.get("timeInRole", {})
        if tir:
            sd = tir.get("startDate", {})
            if sd:
                time_in_role = f"{sd.get('month',0):02d}/{sd.get('year',0)}"
        return {
            "dripify_lead_id":    str(d.get("id", "")),
            "phone":              d.get("phone", "") or "",
            "website":            d.get("website", "") or "",
            "industry":           d.get("industry", "") or "",
            "top_skill":          d.get("topSkill", "") or "",
            "time_in_role":       time_in_role,
            "is_premium":         bool(d.get("premium", False)),
            "responded":          bool(d.get("responded", False)),
            "company_employees":  int((d.get("companyResponse") or {}).get("numberOfEmployees") or 0),
            "linkedin_public_id": d.get("publicId", "") or "",
            "campaign_name":      camp.get("campaign", {}).get("name", "") if camp else "",
            "campaign_status":    camp.get("leadInCampaignStatus", "") if camp else "",
            "campaign_step":      camp.get("sequenceItemStatus", "") if camp else "",
        }

    def enrich_all_contacts(self, db) -> dict:
        """Fetch all conversations from Dripify API, enrich every contact in Supabase."""
        if not self._ensure_token():
            return {"error": "Login fehlgeschlagen"}

        # Load all contacts into memory for fast matching
        all_contacts = db.table("contacts").select("id,dripify_contact_id").execute().data
        # Build map: stored_short_id -> contact_uuid
        contact_map = {
            c["dripify_contact_id"]: c["id"]
            for c in all_contacts
            if c.get("dripify_contact_id")
        }
        log.info("Enriching %d contacts…", len(contact_map))

        summary = {"enriched": 0, "skipped": 0}
        page_num = 0
        while page_num < 20:
            url = f"{BASE}/api/messaging/conversations?archived=false&size=50&page={page_num}"
            r = httpx.get(url, headers=self._headers(), timeout=30)
            if r.status_code != 200:
                break
            data = r.json()
            items = data.get("content", [])
            for item in items:
                lc = item.get("linkedinConversation", {})
                full_id = lc.get("id", "")
                lead_id = item.get("leadInUserId")
                if not full_id or not lead_id:
                    continue
                # Match: find a stored short_id that is a prefix of the Dripify full_id
                contact_id = None
                for short_id, cid in contact_map.items():
                    if full_id.startswith(short_id):
                        contact_id = cid
                        break
                if not contact_id:
                    summary["skipped"] += 1
                    continue
                enriched = self.get_lead_data(lead_id)
                if enriched:
                    try:
                        db.table("contacts").update(enriched).eq("id", contact_id).execute()
                        summary["enriched"] += 1
                        log.info("Enriched: %s", contact_id)
                    except Exception as e:
                        log.warning("Enrich failed %s: %s", contact_id, e)
                        summary["skipped"] += 1
            if data.get("last", True):
                break
            page_num += 1
        return summary

    # ── Send ────────────────────────────────────────────────────────────────
    def send_message(self, dripify_contact_id: str, text: str) -> dict:
        """Send a message. dripify_contact_id can be the short or full conversation ID."""
        if not self._ensure_token():
            return {"ok": False, "error": "Login fehlgeschlagen"}

        # Resolve short → full ID
        full_id = dripify_contact_id
        if len(dripify_contact_id) < 50:  # short ID
            full_id = self.get_full_conversation_id(dripify_contact_id)
            if not full_id:
                # Token might be expired — re-login once
                log.warning("Full ID not found, trying re-login …")
                self._token = None
                if not self._login_playwright():
                    return {"ok": False, "error": f"Conversation {dripify_contact_id} nicht gefunden"}
                full_id = self.get_full_conversation_id(dripify_contact_id)
                if not full_id:
                    return {"ok": False, "error": f"Conversation {dripify_contact_id} nicht gefunden"}

        url = f"{BASE}/api/messaging/conversations/{full_id}/events"
        payload = {"message": text, "attachments": []}

        try:
            r = httpx.post(url, json=payload, headers=self._headers(), timeout=30)
            if r.status_code == 401:
                # Token expired — re-login and retry once
                log.warning("401 — token expired, re-login …")
                self._token = None
                if not self._login_playwright():
                    return {"ok": False, "error": "Re-login fehlgeschlagen"}
                r = httpx.post(url, json=payload, headers=self._headers(), timeout=30)

            if r.status_code in (200, 201):
                log.info("Sent via API to %s", full_id[:30])
                return {"ok": True}
            else:
                return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:200]}"}

        except Exception as e:
            log.exception("API send failed: %s", e)
            return {"ok": False, "error": str(e)}
