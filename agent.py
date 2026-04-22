"""
Core agent loop: Playwright scrapes Dripify → Emma decides → reply sent.
"""
from __future__ import annotations
import logging
from dripify.client import DripifyClient, DripifyMessage
from emma.layers import LayerScores
from emma.signals import detect_signals, detect_decision_type, apply_signals
from emma.decision_engine import determine_blocker, evaluate_flow_mode
from emma.interventions import map_intervention
from emma.flow import build_emma_instruction
from database import repositories as db
from database.client import get_db

from openai_client import assistant as openai_assistant

log = logging.getLogger(__name__)

# Single browser instance — reused across cycles to avoid repeated logins
_dripify: DripifyClient | None = None


def get_dripify() -> DripifyClient:
    global _dripify
    if _dripify is None:
        _dripify = DripifyClient()
        _dripify.start()
    return _dripify


def _scores_from_state(state: db.EmmaState) -> LayerScores:
    return LayerScores(
        state_score=state.state_score,
        clarity_score=state.clarity_score,
        ease_score=state.ease_score,
        trust_score=state.trust_score,
        momentum_score=state.momentum_score,
        authority_score=state.authority_score,
        authority_confidence=state.authority_confidence,
        decision_type=state.decision_type,
    )


def _state_from_scores(state: db.EmmaState, scores: LayerScores) -> db.EmmaState:
    state.state_score = scores.state_score
    state.clarity_score = scores.clarity_score
    state.ease_score = scores.ease_score
    state.trust_score = scores.trust_score
    state.momentum_score = scores.momentum_score
    state.authority_score = scores.authority_score
    state.authority_confidence = scores.authority_confidence
    state.decision_type = scores.decision_type
    return state


def process_message(dripify: DripifyClient, msg: DripifyMessage):
    log.info("Processing message from %s", msg.linkedin_name)

    contact      = db.get_or_create_contact(msg.contact_id, msg.linkedin_name, msg.campaign_id)
    conversation = db.get_or_create_conversation(contact.id)
    emma_state   = db.load_emma_state(contact.id)

    # ── Emma signal + decision ─────────────────────────────────────────────────
    scores  = _scores_from_state(emma_state)
    signals = detect_signals(msg.text)
    scores  = apply_signals(scores, signals)
    dtype   = detect_decision_type(msg.text)
    if dtype:
        scores.decision_type = dtype

    prev_blocker = emma_state.current_blocker
    blocker      = determine_blocker(scores)
    intervention = map_intervention(blocker, scores, emma_state.flow_mode)
    flow_mode    = evaluate_flow_mode(prev_blocker, blocker, scores)

    log.info("Emma | blocker=%s intervention=%s flow=%s", blocker, intervention, flow_mode)

    # ── Generate reply ─────────────────────────────────────────────────────────
    turn             = conversation.turn_count + 1
    emma_instruction = build_emma_instruction(blocker, intervention, scores, flow_mode, turn)
    thread_id        = openai_assistant.get_or_create_thread(conversation.openai_thread_id)

    # Conversation history aus DB für Kontext
    history_rows = (
        get_db().table("agent_log")
        .select("incoming_message,outgoing_message")
        .eq("contact_id", contact.id)
        .order("turn", desc=False)
        .execute().data
    )
    history = []
    for row in history_rows:
        if row.get("incoming_message"):
            history.append({"role": "user", "content": row["incoming_message"]})
        if row.get("outgoing_message"):
            history.append({"role": "assistant", "content": row["outgoing_message"]})

    reply = openai_assistant.run_turn(
        thread_id=thread_id,
        prospect_message=msg.text,
        emma_instruction=emma_instruction,
        conversation_history=history,
    )

    # ── Send reply via Playwright ──────────────────────────────────────────────
    dripify.send_reply(msg.conversation_id, reply)

    # ── Persist ────────────────────────────────────────────────────────────────
    emma_state = _state_from_scores(emma_state, scores)
    emma_state.current_blocker      = blocker
    emma_state.current_intervention = intervention
    emma_state.flow_mode            = flow_mode

    db.save_emma_state(emma_state)
    db.update_conversation(conversation, thread_id=thread_id, last_message_id=msg.message_id)
    db.log_turn(
        contact_id=contact.id, turn=turn,
        incoming_message=msg.text, blocker=blocker,
        intervention=intervention, outgoing_message=reply,
        flow_mode=flow_mode, layer_snapshot=scores.to_dict(),
    )
    log.info("Turn %d complete for %s", turn, msg.linkedin_name)


def run_agent_cycle():
    """One full poll-and-process cycle. Called by the scheduler."""
    log.info("Agent cycle started")
    dripify = get_dripify()

    try:
        # Load known message IDs to skip already-processed messages
        known_ids: set[str] = set()
        result = get_db().table("conversations").select("last_dripify_message_id").execute()
        for row in result.data:
            mid = row.get("last_dripify_message_id")
            if mid:
                known_ids.add(mid)

        new_messages = dripify.get_new_incoming_messages(known_ids)
        log.info("Found %d new message(s)", len(new_messages))

        for msg in new_messages:
            if not msg.text.strip():
                continue
            try:
                process_message(dripify, msg)
            except Exception as exc:
                log.exception("Error processing message from %s: %s", msg.linkedin_name, exc)

    except Exception as exc:
        log.exception("Agent cycle failed: %s", exc)

    log.info("Agent cycle complete")
