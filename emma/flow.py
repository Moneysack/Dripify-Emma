"""
Builds the per-turn Emma decision context sent to the OpenAI Assistant.
Combines blocker, intervention, decision type, layer state, and flow mode
into a structured system instruction block.
"""
from __future__ import annotations
from emma.layers import LayerScores
from emma.interventions import get_intervention_instruction

# Gate status labels
def _gate_status(scores: LayerScores) -> str:
    gates = []
    from emma.layers import TRUST_GATE, EASE_GATE, MOMENTUM_GATE, AUTHORITY_GATE
    if scores.trust_score < TRUST_GATE:
        gates.append(f"TRUST GATE AKTIV ({scores.trust_score:.1f})")
    if scores.ease_score < EASE_GATE:
        gates.append(f"EASE GATE AKTIV ({scores.ease_score:.1f})")
    if scores.momentum_score < MOMENTUM_GATE:
        gates.append(f"MOMENTUM GATE AKTIV ({scores.momentum_score:.1f})")
    if scores.authority_score < AUTHORITY_GATE:
        gates.append(f"AUTHORITY GATE AKTIV ({scores.authority_score:.1f})")
    return ", ".join(gates) if gates else "Keine Gates aktiv"


def build_emma_instruction(
    blocker: str,
    intervention: str,
    scores: LayerScores,
    flow_mode: str,
    turn: int,
) -> str:
    """Return the [EMMA DECISION] block injected before each assistant run."""
    instruction_text = get_intervention_instruction(intervention)
    gate_info = _gate_status(scores)

    # Escalation guard
    gates_active = gate_info != "Keine Gates aktiv"
    escalation_rule = (
        "KEINE Eskalation. KEIN Pitch. KEIN Closing." if gates_active
        else "Eskalation möglich wenn Movement vorhanden."
    )

    return f"""[EMMA DECISION — Turn {turn}]
Blocker         : {blocker}
Intervention    : {intervention}
Flow Mode       : {flow_mode}
Decision Type   : {scores.decision_type}
Gates           : {gate_info}

Layer Scores:
  State      {scores.state_score:.1f} | Clarity {scores.clarity_score:.1f}
  Ease       {scores.ease_score:.1f} | Trust   {scores.trust_score:.1f}
  Momentum   {scores.momentum_score:.1f} | Authority {scores.authority_score:.1f} (conf: {scores.authority_confidence:.2f})

Instruktion:
{instruction_text}

Regeln für diese Antwort:
- {escalation_rule}
- Maximal EINE Frage ODER ein klarer nächster Schritt.
- Kein Mehrfachziel. Kein doppeltes Problem öffnen.
- Sprache: klar, menschlich, respektvoll. Kein Corporate-Speak.
- Länge: maximal 3-4 Sätze."""
