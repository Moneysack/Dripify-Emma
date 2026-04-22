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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

from database.client import get_db
from config import settings

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
    """Store a manual outgoing message and update Emma layer scores."""
    db = get_db()
    text = payload.text.strip()
    if not text:
        raise HTTPException(400, "Empty message")

    # Store outgoing message
    db.table("messages").insert({
        "contact_id": contact_id,
        "direction": "outgoing",
        "text": text,
        "sent_to_dripify": False,
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
        "blocker": blocker,
        "intervention": intervention,
        "flow_mode": flow_mode,
        "scores": scores.to_dict(),
    })


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
    p = Path(__file__).parent / "dashboard.html"
    return HTMLResponse(p.read_text(encoding="utf-8")) if p.exists() else HTMLResponse("dashboard.html not found", 404)


# ── Auto-sync scheduler ────────────────────────────────────────────────────────
@app.on_event("startup")
async def start_scheduler():
    """Start APScheduler to sync Dripify inbox every 5 minutes."""
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
