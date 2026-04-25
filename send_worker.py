"""
Send Worker — lokal starten: python send_worker.py
Prüft alle 5 Sekunden die pending_sends Queue und sendet via Dripify REST API.
Login via Playwright einmalig beim Start (Bearer-Token cachen).
"""
from __future__ import annotations
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("worker")

from config import settings
from database.client import get_db

INTERVAL = 5  # seconds between queue checks


class Worker:
    def __init__(self):
        self.db = get_db()
        from dripify.api_client import DripifyApiClient
        self.client = DripifyApiClient(settings.dripify_email, settings.dripify_password)

    # ── Drain queue ──────────────────────────────────────────────────────────
    def drain(self):
        pending = (
            self.db.table("pending_sends")
            .select("*")
            .eq("status", "pending")
            .execute()
            .data
        )
        if not pending:
            return

        log.info("Queue: %d Nachricht(en)", len(pending))
        for p in pending:
            did  = p.get("dripify_contact_id", "")
            text = p.get("text", "")
            pid  = p["id"]
            if not did or not text:
                continue

            log.info("  -> %s | %s", did[:25], repr(text[:55]))
            result = self.client.send_message(did, text)

            if result.get("ok"):
                self.db.table("pending_sends").update(
                    {"status": "sent", "sent_at": "now()"}
                ).eq("id", pid).execute()
                try:
                    self.db.table("messages").update({"sent_to_dripify": True}).eq(
                        "contact_id", p["contact_id"]
                    ).eq("text", text).eq("direction", "outgoing").execute()
                except Exception:
                    pass
                log.info("  ✓ Gesendet")
            else:
                err = result.get("error", "Unbekannter Fehler")
                self.db.table("pending_sends").update(
                    {"status": "failed", "error_msg": err}
                ).eq("id", pid).execute()
                log.warning("  ✗ Fehler: %s", err)

            time.sleep(1)

    # ── Main loop ────────────────────────────────────────────────────────────
    def run(self):
        log.info("=== Send Worker gestartet (alle %ds) ===", INTERVAL)
        log.info("Login …")
        if not self.client._ensure_token():
            log.error("Login fehlgeschlagen. Beende.")
            return
        log.info("Bereit.")

        errors = 0
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
                    log.info("Zu viele Fehler — Token erneuern …")
                    self.client._token = None
                    self.client._ensure_token()
                    errors = 0

            time.sleep(INTERVAL)

        log.info("Worker gestoppt.")


if __name__ == "__main__":
    Worker().run()
