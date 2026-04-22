from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from database.client import get_db


# ─── Data models ──────────────────────────────────────────────────────────────

@dataclass
class Contact:
    id: str
    dripify_contact_id: str
    linkedin_name: str
    campaign_id: str


@dataclass
class Conversation:
    id: str
    contact_id: str
    openai_thread_id: Optional[str]
    turn_count: int
    last_dripify_message_id: Optional[str]


@dataclass
class EmmaState:
    contact_id: str
    state_score: float = 5.0
    clarity_score: float = 5.0
    ease_score: float = 5.0
    trust_score: float = 5.0
    momentum_score: float = 5.0
    authority_score: float = 5.0
    authority_confidence: float = 0.5
    decision_type: str = "MIXED"
    current_blocker: Optional[str] = None
    current_intervention: Optional[str] = None
    flow_mode: str = "HOLD"
    id: Optional[str] = None


# ─── Contacts ─────────────────────────────────────────────────────────────────

def get_or_create_contact(
    dripify_contact_id: str,
    linkedin_name: str,
    campaign_id: str,
) -> Contact:
    db = get_db()
    result = (
        db.table("contacts")
        .select("*")
        .eq("dripify_contact_id", dripify_contact_id)
        .execute()
    )
    if result.data:
        row = result.data[0]
        return Contact(**{k: row[k] for k in ("id", "dripify_contact_id", "linkedin_name", "campaign_id")})

    insert = db.table("contacts").insert({
        "dripify_contact_id": dripify_contact_id,
        "linkedin_name": linkedin_name,
        "campaign_id": campaign_id,
    }).execute()
    row = insert.data[0]
    return Contact(**{k: row[k] for k in ("id", "dripify_contact_id", "linkedin_name", "campaign_id")})


# ─── Conversations ─────────────────────────────────────────────────────────────

def get_or_create_conversation(contact_id: str) -> Conversation:
    db = get_db()
    result = (
        db.table("conversations")
        .select("*")
        .eq("contact_id", contact_id)
        .execute()
    )
    if result.data:
        row = result.data[0]
        return Conversation(
            id=row["id"],
            contact_id=row["contact_id"],
            openai_thread_id=row.get("openai_thread_id"),
            turn_count=row.get("turn_count", 0),
            last_dripify_message_id=row.get("last_dripify_message_id"),
        )

    insert = db.table("conversations").insert({"contact_id": contact_id}).execute()
    row = insert.data[0]
    return Conversation(
        id=row["id"],
        contact_id=row["contact_id"],
        openai_thread_id=None,
        turn_count=0,
        last_dripify_message_id=None,
    )


def update_conversation(conv: Conversation, thread_id: str | None = None, last_message_id: str | None = None):
    db = get_db()
    payload: dict = {
        "turn_count": conv.turn_count + 1,
        "last_message_at": datetime.utcnow().isoformat(),
    }
    if thread_id:
        payload["openai_thread_id"] = thread_id
    if last_message_id:
        payload["last_dripify_message_id"] = last_message_id

    db.table("conversations").update(payload).eq("id", conv.id).execute()


# ─── Emma State ───────────────────────────────────────────────────────────────

def load_emma_state(contact_id: str) -> EmmaState:
    db = get_db()
    result = (
        db.table("emma_state")
        .select("*")
        .eq("contact_id", contact_id)
        .execute()
    )
    if result.data:
        row = result.data[0]
        return EmmaState(
            id=row["id"],
            contact_id=row["contact_id"],
            state_score=row["state_score"],
            clarity_score=row["clarity_score"],
            ease_score=row["ease_score"],
            trust_score=row["trust_score"],
            momentum_score=row["momentum_score"],
            authority_score=row["authority_score"],
            authority_confidence=row["authority_confidence"],
            decision_type=row["decision_type"],
            current_blocker=row.get("current_blocker"),
            current_intervention=row.get("current_intervention"),
            flow_mode=row.get("flow_mode", "HOLD"),
        )

    insert = db.table("emma_state").insert({"contact_id": contact_id}).execute()
    row = insert.data[0]
    return EmmaState(id=row["id"], contact_id=contact_id)


def save_emma_state(state: EmmaState):
    db = get_db()
    payload = {
        "state_score": state.state_score,
        "clarity_score": state.clarity_score,
        "ease_score": state.ease_score,
        "trust_score": state.trust_score,
        "momentum_score": state.momentum_score,
        "authority_score": state.authority_score,
        "authority_confidence": state.authority_confidence,
        "decision_type": state.decision_type,
        "current_blocker": state.current_blocker,
        "current_intervention": state.current_intervention,
        "flow_mode": state.flow_mode,
        "updated_at": datetime.utcnow().isoformat(),
    }
    db.table("emma_state").update(payload).eq("contact_id", state.contact_id).execute()


# ─── Agent Log ────────────────────────────────────────────────────────────────

def log_turn(
    contact_id: str,
    turn: int,
    incoming_message: str,
    blocker: str,
    intervention: str,
    outgoing_message: str,
    flow_mode: str,
    layer_snapshot: dict,
):
    db = get_db()
    db.table("agent_log").insert({
        "contact_id": contact_id,
        "turn": turn,
        "incoming_message": incoming_message,
        "blocker": blocker,
        "intervention": intervention,
        "outgoing_message": outgoing_message,
        "flow_mode": flow_mode,
        "layer_snapshot": layer_snapshot,
    }).execute()
