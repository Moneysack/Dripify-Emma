"""
Emma LLM Analyzer — scans a full conversation with GPT-4o and returns
rich 7-layer Emma analysis including state clusters, confidence, pain points.

Based on the Emma project's backcasting.ts + emma-knowledge.ts logic.
"""
from __future__ import annotations
import json
import logging
from openai import OpenAI
from config import settings

log = logging.getLogger(__name__)

# ── Emma Analysis System Prompt ───────────────────────────────────────────────
EMMA_ANALYSIS_SYSTEM_PROMPT = """Du bist das Emma-Analyse-Framework. Deine Aufgabe ist es, ein LinkedIn-Verkaufsgespräch
zu analysieren und einen vollständigen Emma-State zurückzugeben.

## EMMA 7-LAYER FRAMEWORK

Bewerte jeden Layer auf einer Skala von 0-10 + Confidence (0.0-1.0):

**TRUST** (Vertrauen): Wie sicher, offen und bereit ist der Prospect?
- 0-3: Starke Skepsis, Ablehnung, defensives Verhalten
- 4-6: Neutral bis leicht offen, vorsichtig
- 7-10: Offen, vertraut, kooperativ

**CLARITY** (Klarheit): Wie klar versteht der Prospect sein eigenes Problem?
- 0-3: Kein Problembewusstsein, symptomatisch, trivialisiert
- 4-6: Erkennt Symptome, keine Kausalität
- 7-10: Versteht Ursachen und Muster, strukturiertes Problembild

**EASE** (Leichtigkeit): Wie viel Kapazität/Zeit/Energie hat der Prospect?
- 0-3: Überlastet, keine Zeit, keine Kapazität
- 4-6: Eingeschränkt, aber prinzipiell zugänglich
- 7-10: Entspannt, kapazitiv frei, aufnahmefähig

**TRUST** Gate: < 5 → KEIN Pitch, KEIN Druck, KEINE Aktivierung
**EASE** Gate: < 4 → Alles reduzieren, keine neuen Konzepte
**MOMENTUM** Gate: < 4 → KEINE Eskalation, KEIN Closing
**AUTHORITY** Gate: < 5 → KEIN Closing, KEINE Kaufaufforderung

**TRUST** (Vertrauen) 0-10
**CLARITY** (Klarheit) 0-10
**AUTHORITY** (Autorität/Entscheidungsmacht) 0-10
**EASE** (Leichtigkeit/Kapazität) 0-10
**MOMENTUM** (Energie/Aktivierung) 0-10
**STATE** (Problembewusstsein-Reife) 0-10
**DECISION_TYPE**: THINKER / DOER / VISUAL / SPEAKER / MIXED

## STATE CLUSTER (Reifegrad des Prospects)
- **S0**: Kein Problembewusstsein (State<4, Clarity<4, Momentum<4)
- **S1**: Passiv-latent (State 4-6, Clarity 4-5, Momentum<4)
- **S2**: Aktivierungslücke (State≥5, Trust≥5, Clarity≥5, Momentum≥4)
- **S3**: Begrenzte Ausführung (State≥6, Trust≥6, Clarity≥6, Momentum≥5)
- **S4**: Commitment-bereit (Trust≥7, Clarity≥7, Momentum≥6, Authority≥6)
- **S5**: Multiplikator (Trust≥8, Clarity≥8, Momentum≥7, Authority≥7)

## BLOCKER LOGIC (Gate-Priorität: Trust > Ease > Momentum > Authority)
1. Trust < 5 → Blocker = TRUST
2. Ease < 4 → Blocker = EASE
3. Momentum < 4 → Blocker = MOMENTUM
4. Authority < 5 → Blocker = AUTHORITY
5. Sonst → Layer mit dem niedrigsten Score (STATE oder CLARITY)

## INTERVENTION MAPPING
- STATE → MIRROR oder REFRAME
- CLARITY → CLARIFY oder STRUCTURE
- EASE → REDUCE
- TRUST → SAFETY oder TRUST_BUILD
- MOMENTUM → ACTIVATE
- AUTHORITY → ROUTE

## OUTPUT MODE
- **CRITICAL**: Trust ≤ 3 oder Ease ≤ 2 → Kein Pitch, kein Druck
- **SAFE**: Trust 3-4 → Nur Sicherheit aufbauen
- **UNCERTAIN**: Confidence < 0.4 → Nur weiche Klärungsfragen
- **ESCALATION_ELIGIBLE**: Trust≥7, Clarity≥7, Momentum≥6, Authority≥5
- **NORMAL**: Alles andere

## MOVEMENT SCORE (0-5)
Wie stark hat sich der Prospect in Richtung Öffnung/Handlung bewegt?
0 = keine Bewegung, 1 = einmalig, 2 = wiederholt, 3 = stabil

## PAIN POINTS
Erkenne explizit genannte oder implizit erkennbare Schmerzpunkte.
Severity: hoch / mittel / niedrig
Zitiere die exakte Aussage des Prospects wenn möglich.

## ANTWORTFORMAT (streng JSON)
Gib NUR dieses JSON zurück, keine Erklärungen:

{
  "trust": 0-10,
  "trust_conf": 0.0-1.0,
  "clarity": 0-10,
  "clarity_conf": 0.0-1.0,
  "authority": 0-10,
  "authority_conf": 0.0-1.0,
  "ease": 0-10,
  "ease_conf": 0.0-1.0,
  "momentum": 0-10,
  "momentum_conf": 0.0-1.0,
  "state_score": 0-10,
  "state_conf": 0.0-1.0,
  "decision_type": "THINKER|DOER|VISUAL|SPEAKER|MIXED",
  "state_cluster": "S0|S1|S2|S3|S4|S5",
  "blocker": "TRUST|CLARITY|AUTHORITY|EASE|MOMENTUM|STATE|null",
  "intervention": "MIRROR|REFRAME|SAFETY|TRUST_BUILD|CLARIFY|REDUCE|STRUCTURE|ACTIVATE|ROUTE|ESCALATION|null",
  "output_mode": "CRITICAL|SAFE|UNCERTAIN|NORMAL|ESCALATION_ELIGIBLE",
  "movement_score": 0-5,
  "movement_stability": "M0|M1|M2|M3",
  "escalation_eligible": true|false,
  "prospect_summary": "2-3 Sätze über den Prospect und seinen aktuellen State",
  "pain_points": [
    {"pain": "Beschreibung des Schmerzpunkts", "severity": "hoch|mittel|niedrig", "quote": "exaktes Zitat oder null"}
  ]
}"""


def _build_conversation_text(messages: list[dict]) -> str:
    """Format messages as a readable conversation transcript."""
    lines = []
    for m in messages:
        role = "Emma" if m.get("direction") == "outgoing" else "Prospect"
        text = (m.get("text") or "").strip()
        if text:
            lines.append(f"{role}: {text}")
    return "\n".join(lines)


def analyze_conversation(messages: list[dict]) -> dict:
    """
    Run the full Emma LLM analysis on a conversation.
    Returns a dict matching the emma_state extended schema.
    """
    if not messages:
        return _default_result()

    # Only use incoming messages for analysis if there are no outgoing
    # (some contacts were synced before replies were sent)
    convo_text = _build_conversation_text(messages)
    if not convo_text.strip():
        return _default_result()

    client = OpenAI(api_key=settings.openai_api_key)

    user_message = f"""Analysiere dieses LinkedIn-Verkaufsgespräch mit dem Emma-Framework:

---
{convo_text}
---

Gib deine Analyse als JSON zurück."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": EMMA_ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=800,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)
        return _normalize(result)
    except Exception as e:
        log.error("Emma LLM analysis failed: %s", e)
        return _default_result()


def analyze_phases(messages: list[dict]) -> dict:
    """
    Split conversation into 3 phases and analyze each independently.
    Returns history analysis with trend and turning point.
    """
    if len(messages) < 3:
        return {"phases": [], "overall_trend": "stabil", "key_turning_point": None}

    # Split into thirds
    n = len(messages)
    third = max(1, n // 3)
    phase_msgs = [
        messages[:third],
        messages[third:third * 2],
        messages[third * 2:],
    ]

    phases = []
    layer_keys = ["trust", "clarity", "authority", "ease", "momentum", "state_score"]
    prev_scores = None

    for i, phase in enumerate(phase_msgs):
        result = analyze_conversation(phase)
        scores = {k: result.get(k, 5.0) for k in layer_keys}

        deltas = {}
        if prev_scores:
            for k in layer_keys:
                deltas[k] = round(scores[k] - prev_scores[k], 1)

        phases.append({
            "label": ["Beginn", "Mitte", "Aktuell"][i],
            "message_count": len(phase),
            "scores": {k: round(scores[k], 1) for k in layer_keys},
            "deltas": deltas,
            "blocker": result.get("blocker"),
            "output_mode": result.get("output_mode", "NORMAL"),
            "pain_points": result.get("pain_points", []),
        })
        prev_scores = scores

    # Compute overall trend from first to last phase
    avg_delta = 0.0
    if len(phases) >= 2:
        first = phases[0]["scores"]
        last = phases[-1]["scores"]
        total = sum(last[k] - first[k] for k in layer_keys)
        avg_delta = total / len(layer_keys)

    trend = "positiv" if avg_delta >= 1.5 else "negativ" if avg_delta <= -1.5 else "gemischt" if abs(avg_delta) > 0.3 else "stabil"

    # Turning point: phase with the biggest positive change
    turning_point = None
    if len(phases) >= 2:
        best_phase = max(phases[1:], key=lambda p: sum(p["deltas"].values()) if p["deltas"] else 0, default=None)
        if best_phase and best_phase["deltas"]:
            best_layer = max(best_phase["deltas"], key=lambda k: best_phase["deltas"][k])
            d = best_phase["deltas"][best_layer]
            if d > 0.5:
                turning_point = f"{best_phase['label']}: {best_layer} +{d}"

    return {
        "phases": phases,
        "overall_trend": trend,
        "key_turning_point": turning_point,
        "avg_delta": round(avg_delta, 2),
    }


def _normalize(r: dict) -> dict:
    """Clamp and validate all fields."""
    def f(k, default=5.0): return float(r.get(k, default))
    def c(k): return max(0.0, min(1.0, float(r.get(k, 0.5))))

    return {
        "trust_score":       max(0, min(10, f("trust"))),
        "clarity_score":     max(0, min(10, f("clarity"))),
        "ease_score":        max(0, min(10, f("ease"))),
        "momentum_score":    max(0, min(10, f("momentum"))),
        "authority_score":   max(0, min(10, f("authority"))),
        "state_score":       max(0, min(10, f("state_score"))),
        "trust_conf":        c("trust_conf"),
        "clarity_conf":      c("clarity_conf"),
        "ease_conf":         c("ease_conf"),
        "momentum_conf":     c("momentum_conf"),
        "authority_conf":    c("authority_conf"),
        "authority_confidence": c("authority_conf"),
        "state_conf":        c("state_conf"),
        "decision_type":     r.get("decision_type", "MIXED"),
        "state_cluster":     r.get("state_cluster", "S0"),
        "current_blocker":   r.get("blocker"),
        "current_intervention": r.get("intervention"),
        "output_mode":       r.get("output_mode", "NORMAL"),
        "movement_score":    int(r.get("movement_score", 0)),
        "movement_stability": r.get("movement_stability", "M0"),
        "escalation_eligible": bool(r.get("escalation_eligible", False)),
        "prospect_summary":  r.get("prospect_summary", ""),
        "pain_points":       r.get("pain_points", []),
        "flow_mode":         _output_mode_to_flow(r.get("output_mode", "NORMAL")),
    }


def _output_mode_to_flow(mode: str) -> str:
    if mode in ("CRITICAL", "SAFE"):
        return "RECOVERY"
    if mode == "ESCALATION_ELIGIBLE":
        return "ADVANCE"
    return "HOLD"


def _default_result() -> dict:
    return _normalize({})
