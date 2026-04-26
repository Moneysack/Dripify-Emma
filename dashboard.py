"""
Emma Dashboard — FastAPI backend.
Run: python dashboard.py  ->  http://localhost:7777
"""
from __future__ import annotations
import json, logging, os, sys, threading
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

# Read HTML at import time — ensures Vercel bundles the file (same trick as Ask-EINO)
_HTML_PATH = Path(__file__).parent / "dashboard.html"
_DASHBOARD_HTML: str = _HTML_PATH.read_text(encoding="utf-8") if _HTML_PATH.exists() else "<h1>dashboard.html not found</h1>"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

try:
    from database.client import get_db
    from config import settings
except Exception as _cfg_err:
    import logging as _l
    _l.getLogger(__name__).error("Config/DB import error: %s", _cfg_err)
    settings = None  # type: ignore
    def get_db():  # type: ignore
        from fastapi import HTTPException
        raise HTTPException(500, f"Configuration error: {_cfg_err}")

app = FastAPI(title="Emma Dashboard")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_sync_status = {"running": False, "last": None}


# ── helpers ────────────────────────────────────────────────────────────────────
def _ampel(score: float) -> str:
    if score < 4.0:  return "red"
    if score < 6.5:  return "yellow"
    return "green"

def _overall(state: dict) -> str:
    scores = [state.get(k, 5) for k in
              ["state_score","clarity_score","ease_score","trust_score","momentum_score","authority_score"]]
    return _ampel(sum(scores) / len(scores))


# ── contacts list ──────────────────────────────────────────────────────────────
@app.get("/api/contacts")
def list_contacts():
    db = get_db()

    # 4 bulk queries instead of 3 per contact
    contacts = db.table("contacts").select("*").execute().data
    states    = db.table("emma_state").select("*").execute().data
    convs     = db.table("conversations").select("contact_id,turn_count").execute().data
    all_msgs  = db.table("messages").select("contact_id,text,direction,created_at") \
        .order("created_at", desc=True).execute().data

    # Index by contact_id
    state_by  = {s["contact_id"]: s for s in states}
    conv_by   = {c["contact_id"]: c for c in convs}
    # Keep only latest message per contact
    last_msg_by: dict = {}
    for m in all_msgs:
        cid = m["contact_id"]
        if cid not in last_msg_by:
            last_msg_by[cid] = m

    result = []
    for c in contacts:
        cid   = c["id"]
        state = state_by.get(cid, {})
        conv  = conv_by.get(cid, {})
        lm    = last_msg_by.get(cid, {})
        result.append({
            "id":              cid,
            "linkedin_name":   c.get("linkedin_name", "?"),
            "campaign_id":     c.get("campaign_id", ""),
            "avatar_url":      c.get("avatar_url", ""),
            "title":           c.get("title", ""),
            "company_name":    c.get("company_name", ""),
            "location":        c.get("location", ""),
            "linkedin_url":    c.get("linkedin_url", ""),
            "dripify_contact_id": c.get("dripify_contact_id", ""),
            "email":             c.get("email", ""),
            "connections_count": c.get("connections_count", ""),
            "country":           c.get("country", ""),
            # enriched fields
            "phone":             c.get("phone", ""),
            "website":           c.get("website", ""),
            "industry":          c.get("industry", ""),
            "top_skill":         c.get("top_skill", ""),
            "time_in_role":      c.get("time_in_role", ""),
            "is_premium":        c.get("is_premium", False),
            "responded":         c.get("responded", False),
            "company_employees": c.get("company_employees", 0),
            "campaign_name":     c.get("campaign_name", ""),
            "campaign_status":   c.get("campaign_status", ""),
            "campaign_step":     c.get("campaign_step", ""),
            "linkedin_public_id":c.get("linkedin_public_id", ""),
            "created_at":      c.get("created_at", ""),
            "turn_count":      conv.get("turn_count", 0),
            "last_message":    lm.get("text", "")[:80],
            "last_direction":  lm.get("direction", ""),
            "last_message_at": lm.get("created_at", ""),
            "status":          _overall(state),
            "blocker":         state.get("current_blocker", "—"),
            "flow_mode":       state.get("flow_mode", "HOLD"),
            "state":           state,
        })

    # Sort newest message first (mirrors Dripify inbox order)
    result.sort(key=lambda x: x["last_message_at"] or "", reverse=True)
    return JSONResponse(result)


# ── image proxy (LinkedIn CDN images require server-side fetch) ─────────────────
@app.get("/api/img")
async def proxy_image(url: str):
    import httpx
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=8) as client:
            r = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.linkedin.com/",
            })
            from fastapi.responses import Response
            return Response(content=r.content, media_type=r.headers.get("content-type", "image/jpeg"))
    except Exception:
        raise HTTPException(404, "Image not available")


# ── messages for a contact ─────────────────────────────────────────────────────
@app.get("/api/contacts/{contact_id}/messages")
def get_messages(contact_id: str):
    db = get_db()
    rows = db.table("messages").select("*") \
        .eq("contact_id", contact_id).order("created_at", desc=False).execute().data
    return JSONResponse(rows)


# ── emma state for a contact ───────────────────────────────────────────────────
@app.get("/api/contacts/{contact_id}/state")
def get_state(contact_id: str):
    db = get_db()
    rows = db.table("emma_state").select("*").eq("contact_id", contact_id).execute().data
    return JSONResponse(rows[0] if rows else {})


# ── manual send message ────────────────────────────────────────────────────────
class SendPayload(BaseModel):
    text: str

@app.post("/api/contacts/{contact_id}/send")
def send_message(contact_id: str, payload: SendPayload):
    """Send message via Dripify (Playwright) + store in DB + update Emma scores."""
    db = get_db()
    text = payload.text.strip()
    if not text:
        raise HTTPException(400, "Empty message")

    # Lookup dripify_contact_id — try contacts table first, fall back to messages table
    contact_row = db.table("contacts").select("dripify_contact_id").eq("id", contact_id).execute().data
    dripify_id  = (contact_row[0].get("dripify_contact_id") or "").strip() if contact_row else ""

    if not dripify_id:
        # Fallback: dripify_msg_id stored on any message for this contact
        msg_row = db.table("messages").select("dripify_msg_id") \
            .eq("contact_id", contact_id).neq("dripify_msg_id", "").limit(1).execute().data
        if msg_row and msg_row[0].get("dripify_msg_id"):
            dripify_id = msg_row[0]["dripify_msg_id"].strip()
            # Back-fill the contacts table so future lookups are fast
            try:
                db.table("contacts").update({"dripify_contact_id": dripify_id}) \
                    .eq("id", contact_id).execute()
            except Exception:
                pass

    # Send via Playwright (local) or queue (Vercel)
    queued = False
    if not dripify_id:
        dripify_result = {"ok": False, "error": "Dripify-ID fehlt — Sync ausführen"}
    elif _ON_VERCEL:
        # Queue for local worker to pick up during next sync
        try:
            db.table("pending_sends").insert({
                "contact_id": contact_id,
                "dripify_contact_id": dripify_id,
                "text": text,
            }).execute()
            dripify_result = {"ok": True, "queued": True}
            queued = True
        except Exception as e:
            err = str(e)
            if "pending_sends" in err and ("PGRST205" in err or "schema cache" in err.lower()):
                dripify_result = {"ok": False, "error": "SQL-Migration fehlt — bitte add_send_queue.sql in Supabase ausführen"}
            else:
                dripify_result = {"ok": False, "error": f"Queue-Fehler: {err[:120]}"}
    else:
        dripify_result = {"ok": False, "error": "Unbekannter Fehler"}
        try:
            from dripify.sender import send_message as dripify_send
            dripify_result = dripify_send(dripify_id, text)
        except Exception as e:
            dripify_result = {"ok": False, "error": str(e)}

    # Store outgoing message
    db.table("messages").insert({
        "contact_id": contact_id,
        "direction": "outgoing",
        "text": text,
        "sent_to_dripify": dripify_result.get("ok", False) and not queued,
    }).execute()

    # Run Emma analysis on the full conversation so far
    from emma.signals import detect_signals, detect_decision_type, apply_signals
    from emma.decision_engine import determine_blocker, evaluate_flow_mode
    from emma.interventions import map_intervention
    from emma.layers import LayerScores

    state_rows = db.table("emma_state").select("*").eq("contact_id", contact_id).execute().data
    state = state_rows[0] if state_rows else {}

    scores = LayerScores(
        state_score=state.get("state_score", 5),
        clarity_score=state.get("clarity_score", 5),
        ease_score=state.get("ease_score", 5),
        trust_score=state.get("trust_score", 5),
        momentum_score=state.get("momentum_score", 5),
        authority_score=state.get("authority_score", 5),
        authority_confidence=state.get("authority_confidence", 0.5),
        decision_type=state.get("decision_type", "MIXED"),
    )

    # Analyze all incoming messages for layer updates
    msgs = db.table("messages").select("direction,text") \
        .eq("contact_id", contact_id).order("created_at", desc=False).execute().data
    for m in msgs:
        if m["direction"] == "incoming":
            sigs = detect_signals(m["text"])
            scores = apply_signals(scores, sigs)
            dtype = detect_decision_type(m["text"])
            if dtype:
                scores.decision_type = dtype

    prev_blocker = state.get("current_blocker")
    blocker      = determine_blocker(scores)
    intervention = map_intervention(blocker, scores, state.get("flow_mode", "HOLD"))
    flow_mode    = evaluate_flow_mode(prev_blocker, blocker, scores)

    db.table("emma_state").update({
        "state_score":          scores.state_score,
        "clarity_score":        scores.clarity_score,
        "ease_score":           scores.ease_score,
        "trust_score":          scores.trust_score,
        "momentum_score":       scores.momentum_score,
        "authority_score":      scores.authority_score,
        "authority_confidence": scores.authority_confidence,
        "decision_type":        scores.decision_type,
        "current_blocker":      blocker,
        "current_intervention": intervention,
        "flow_mode":            flow_mode,
    }).eq("contact_id", contact_id).execute()

    return JSONResponse({
        "ok": True,
        "sent_to_dripify": dripify_result.get("ok", False) and not queued,
        "queued": queued,
        "send_error": dripify_result.get("error") if not dripify_result.get("ok") else None,
        "blocker": blocker,
        "intervention": intervention,
        "flow_mode": flow_mode,
        "scores": scores.to_dict(),
    })


# ── refresh profile from Dripify ──────────────────────────────────────────────
@app.post("/api/contacts/{contact_id}/refresh-profile")
def refresh_profile(contact_id: str):
    """Re-scrape LinkedIn profile info from the Dripify conversation panel."""
    if _ON_VERCEL:
        raise HTTPException(400, "Profile scraping requires local server")
    db = get_db()
    contact_row = db.table("contacts").select("*").eq("id", contact_id).execute().data
    if not contact_row:
        raise HTTPException(404, "Contact not found")
    c = contact_row[0]
    dripify_id = (c.get("dripify_contact_id") or "").strip()
    if not dripify_id:
        # Fallback: look up from messages
        msg_row = db.table("messages").select("dripify_msg_id") \
            .eq("contact_id", contact_id).neq("dripify_msg_id", "").limit(1).execute().data
        if msg_row and msg_row[0].get("dripify_msg_id"):
            dripify_id = msg_row[0]["dripify_msg_id"].strip()
    if not dripify_id:
        raise HTTPException(400, "Keine Dripify-ID — bitte Sync ausführen")

    from dripify.sender import scrape_profile
    profile = scrape_profile(dripify_id)

    if profile:
        update = {}
        for field in ("avatar_url", "title", "company_name", "location", "linkedin_url", "email", "connections_count"):
            if profile.get(field):
                update[field] = profile[field]
        if update:
            try:
                db.table("contacts").update(update).eq("id", contact_id).execute()
            except Exception as e:
                log.error("Profile update failed: %s", e)

    # Return updated contact
    updated = {**c, **profile}
    return JSONResponse(updated)


# ── AI reply suggestion ────────────────────────────────────────────────────────
@app.get("/api/contacts/{contact_id}/suggest")
def suggest_reply(contact_id: str):
    """Generate an Emma-guided reply via OpenAI and return it for review."""
    from emma.signals import detect_signals, detect_decision_type, apply_signals
    from emma.decision_engine import determine_blocker
    from emma.interventions import map_intervention
    from emma.layers import LayerScores
    from emma.flow import build_emma_instruction
    from openai_client import assistant as openai_assistant

    db_client = get_db()

    # Load current state + messages
    state_rows = db_client.table("emma_state").select("*").eq("contact_id", contact_id).execute().data
    state = state_rows[0] if state_rows else {}

    msgs = db_client.table("messages").select("direction,text").eq("contact_id", contact_id) \
        .order("created_at", desc=False).execute().data

    if not msgs:
        raise HTTPException(400, "Keine Nachrichten vorhanden")

    # Rebuild scores from stored state
    scores = LayerScores(
        state_score         = state.get("state_score", 5),
        clarity_score       = state.get("clarity_score", 5),
        ease_score          = state.get("ease_score", 5),
        trust_score         = state.get("trust_score", 5),
        momentum_score      = state.get("momentum_score", 5),
        authority_score     = state.get("authority_score", 5),
        authority_confidence= state.get("authority_confidence", 0.5),
        decision_type       = state.get("decision_type", "MIXED"),
    )

    blocker      = state.get("current_blocker") or determine_blocker(scores)
    intervention = state.get("current_intervention") or map_intervention(blocker, scores, state.get("flow_mode", "HOLD"))
    flow_mode    = state.get("flow_mode", "HOLD")

    conv_rows = db_client.table("conversations").select("turn_count,openai_thread_id") \
        .eq("contact_id", contact_id).execute().data
    conv  = conv_rows[0] if conv_rows else {}
    turn  = conv.get("turn_count", 0) + 1

    emma_instruction = build_emma_instruction(blocker, intervention, scores, flow_mode, turn)

    # Last incoming message as the user turn for OpenAI
    last_incoming = next((m["text"] for m in reversed(msgs) if m["direction"] == "incoming"), msgs[-1]["text"])

    # Build conversation history (all messages except the last incoming)
    history = []
    for m in msgs:
        if m["text"] == last_incoming and m["direction"] == "incoming":
            continue  # this becomes the user message
        role = "assistant" if m["direction"] == "outgoing" else "user"
        history.append({"role": role, "content": m["text"]})

    try:
        reply = openai_assistant.run_turn(
            thread_id=conv.get("openai_thread_id") or f"contact_{contact_id}",
            prospect_message=last_incoming,
            emma_instruction=emma_instruction,
            conversation_history=history[-20:],
        )
    except Exception as e:
        raise HTTPException(500, f"OpenAI Fehler: {e}")

    return JSONResponse({"reply": reply, "blocker": blocker, "intervention": intervention, "flow_mode": flow_mode})


# ── analyze incoming message (prospect reply) ─────────────────────────────────
class IncomingPayload(BaseModel):
    text: str

@app.post("/api/contacts/{contact_id}/incoming")
def incoming_message(contact_id: str, payload: IncomingPayload):
    """Store incoming message + run Emma analysis."""
    db = get_db()
    text = payload.text.strip()
    if not text:
        raise HTTPException(400, "Empty message")

    db.table("messages").insert({
        "contact_id": contact_id,
        "direction": "incoming",
        "text": text,
    }).execute()

    # Reuse send logic (Emma reacts to incoming too)
    return send_message(contact_id, SendPayload(text=""))


# ── stats ──────────────────────────────────────────────────────────────────────
@app.get("/api/stats")
def get_stats():
    db = get_db()
    contacts = len(db.table("contacts").select("id").execute().data)
    messages = len(db.table("messages").select("id").execute().data)
    states   = db.table("emma_state").select("flow_mode,current_blocker").execute().data
    return {
        "total_contacts": contacts,
        "total_messages": messages,
        "advance_count":  sum(1 for s in states if s.get("flow_mode") == "ADVANCE"),
        "recovery_count": sum(1 for s in states if s.get("flow_mode") == "RECOVERY"),
    }


# ── score trajectory ──────────────────────────────────────────────────────────
@app.get("/api/contacts/{contact_id}/trajectory")
def get_trajectory(contact_id: str):
    """Replay Emma scoring through each message — returns per-turn score evolution."""
    from emma.signals import detect_signals, detect_decision_type, apply_signals
    from emma.decision_engine import determine_blocker
    from emma.layers import LayerScores

    db_client = get_db()
    msgs = (
        db_client.table("messages")
        .select("*")
        .eq("contact_id", contact_id)
        .order("created_at", desc=False)
        .execute()
        .data
    )

    scores = LayerScores()
    LAYER_KEYS = ["state_score", "clarity_score", "ease_score", "trust_score", "momentum_score", "authority_score"]
    history = []

    for msg in msgs:
        prev = {k: getattr(scores, k) for k in LAYER_KEYS}

        if msg["direction"] == "incoming":
            sigs = detect_signals(msg["text"])
            scores = apply_signals(scores, sigs)
            dtype = detect_decision_type(msg["text"])
            if dtype:
                scores.decision_type = dtype

        curr = {k: getattr(scores, k) for k in LAYER_KEYS}
        blocker = determine_blocker(scores)

        changes = {}
        for k in LAYER_KEYS:
            delta = round(curr[k] - prev[k], 2)
            if abs(delta) > 0.01:
                changes[k] = {"from": round(prev[k], 1), "to": round(curr[k], 1), "delta": round(delta, 1)}

        history.append({
            "direction": msg["direction"],
            "text": msg["text"][:200],
            "created_at": msg.get("created_at", ""),
            "scores": {k: round(v, 1) for k, v in curr.items()},
            "blocker": blocker,
            "changes": changes,
        })

    return JSONResponse(history)


# ── LLM Emma analysis ─────────────────────────────────────────────────────────
@app.post("/api/contacts/{contact_id}/analyze")
def analyze_contact(contact_id: str):
    """Run full LLM-based Emma analysis on the conversation and persist results."""
    from emma.analyzer import analyze_conversation
    from datetime import datetime, timezone

    db = get_db()
    msgs = (
        db.table("messages")
        .select("direction,text,created_at")
        .eq("contact_id", contact_id)
        .order("created_at", desc=False)
        .execute()
        .data
    )
    if not msgs:
        raise HTTPException(400, "Keine Nachrichten für diesen Kontakt")

    result = analyze_conversation(msgs)

    ts = datetime.now(timezone.utc).isoformat()
    result["analyzed_at"] = ts

    # Base columns (always exist in schema)
    base_update = {
        "state_score":          result["state_score"],
        "clarity_score":        result["clarity_score"],
        "ease_score":           result["ease_score"],
        "trust_score":          result["trust_score"],
        "momentum_score":       result["momentum_score"],
        "authority_score":      result["authority_score"],
        "authority_confidence": result["authority_confidence"],
        "decision_type":        result["decision_type"],
        "current_blocker":      result["current_blocker"],
        "current_intervention": result["current_intervention"],
        "flow_mode":            result["flow_mode"],
    }

    # Extended columns — only present after running database/add_analyzer_columns.sql
    extended = {col: result[col] for col in (
        "trust_conf","clarity_conf","ease_conf","momentum_conf","state_conf",
        "state_cluster","movement_score","movement_stability","output_mode",
        "escalation_eligible","pain_points","prospect_summary","analyzed_at",
    ) if col in result}

    try:
        db.table("emma_state").update({**base_update, **extended}).eq("contact_id", contact_id).execute()
    except Exception:
        # Fallback: extended columns not yet migrated — save only base
        try:
            db.table("emma_state").update(base_update).eq("contact_id", contact_id).execute()
        except Exception as e2:
            log.error("emma_state update failed: %s", e2)

    return JSONResponse(result)


# ── LLM phase history analysis ────────────────────────────────────────────────
@app.get("/api/contacts/{contact_id}/analyze-history")
def analyze_history(contact_id: str):
    """Split conversation into 3 phases and return trend analysis."""
    from emma.analyzer import analyze_phases

    db = get_db()
    msgs = (
        db.table("messages")
        .select("direction,text,created_at")
        .eq("contact_id", contact_id)
        .order("created_at", desc=False)
        .execute()
        .data
    )
    return JSONResponse(analyze_phases(msgs))


# ── Enrich contacts from Dripify API ──────────────────────────────────────────
_enrich_status = {"running": False, "last": None}

def _run_enrich():
    _enrich_status["running"] = True
    try:
        from dripify.api_client import DripifyApiClient
        client = DripifyApiClient(settings.dripify_email, settings.dripify_password)
        db = get_db()
        result = client.enrich_all_contacts(db)
        _enrich_status["last"] = result
    except Exception as e:
        _enrich_status["last"] = {"error": str(e)}
    finally:
        _enrich_status["running"] = False

@app.post("/api/enrich")
def trigger_enrich():
    """Fetch full lead data from Dripify API and update all contacts."""
    if _enrich_status["running"]:
        return JSONResponse({"status": "already_running"})
    t = threading.Thread(target=_run_enrich, daemon=True)
    t.start()
    return JSONResponse({"status": "started"})

@app.get("/api/enrich/status")
def enrich_status():
    return JSONResponse(_enrich_status)


# ── Dripify sync ───────────────────────────────────────────────────────────────
def _run_sync():
    _sync_status["running"] = True
    try:
        from dripify.sync import DripifySync
        syncer = DripifySync(settings.dripify_email, settings.dripify_password)
        syncer.start()
        result = syncer.sync_all()
        syncer.stop()
        _sync_status["last"] = result
    except Exception as e:
        _sync_status["last"] = {"error": str(e)}
    finally:
        _sync_status["running"] = False

@app.post("/api/sync")
def trigger_sync():
    if _ON_VERCEL:
        return JSONResponse({"status": "not_available", "reason": "Sync runs locally, not on Vercel"})
    if _sync_status["running"]:
        return JSONResponse({"status": "already_running"})
    t = threading.Thread(target=_run_sync, daemon=True)
    t.start()
    return JSONResponse({"status": "started"})

@app.get("/api/sync/status")
def sync_status():
    return JSONResponse(_sync_status)


# ── serve HTML ─────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def serve():
    return HTMLResponse(_DASHBOARD_HTML)


# ── Auto-sync scheduler (local only — disabled on Vercel serverless) ───────────
import os as _os
_ON_VERCEL = bool(_os.environ.get("VERCEL") or _os.environ.get("VERCEL_ENV"))

@app.on_event("startup")
async def start_scheduler():
    """Start APScheduler to sync Dripify inbox every 5 minutes (local only)."""
    if _ON_VERCEL:
        log.info("Vercel environment detected — scheduler disabled (sync runs locally)")
        return
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler(timezone="Europe/Berlin")
        scheduler.add_job(
            _run_sync,
            trigger="interval",
            minutes=5,
            id="dripify_sync",
            max_instances=1,
            misfire_grace_time=60,
        )
        scheduler.start()
        log.info("Scheduler started — Dripify sync every 5 minutes")

        # Run once immediately on startup (in background)
        t = threading.Thread(target=_run_sync, daemon=True)
        t.start()
        log.info("Initial sync started in background")
    except Exception as e:
        log.error("Failed to start scheduler: %s", e)


if __name__ == "__main__":
    uvicorn.run("dashboard:app", host="0.0.0.0", port=4521, reload=False)
