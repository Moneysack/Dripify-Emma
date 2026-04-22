"""
Emma Decision Engine — determines the single dominant blocker.

Gate priority (from Conversation Flow JSONL section 9, Rule 4):
  Trust > Ease > Momentum > Authority

If no gate is active, lowest of STATE vs CLARITY wins.
"""
from __future__ import annotations
from emma.layers import LayerScores, TRUST_GATE, EASE_GATE, MOMENTUM_GATE, AUTHORITY_GATE

AUTHORITY_CONFIDENCE_GATE = 0.4


def determine_blocker(scores: LayerScores) -> str:
    """Return the name of the single dominant blocking layer."""

    # 1. Gate priority
    if scores.trust_score < TRUST_GATE:
        return "TRUST"

    if scores.ease_score < EASE_GATE:
        return "EASE"

    if scores.momentum_score < MOMENTUM_GATE:
        return "MOMENTUM"

    # Authority gate: triggered by low score OR low confidence
    if scores.authority_score < AUTHORITY_GATE or scores.authority_confidence < AUTHORITY_CONFIDENCE_GATE:
        return "AUTHORITY"

    # 2. Progression layers — lowest of STATE vs CLARITY
    if scores.state_score <= scores.clarity_score:
        return "STATE"
    return "CLARITY"


def evaluate_flow_mode(prev_blocker: str | None, new_blocker: str, scores: LayerScores) -> str:
    """
    Determine ADVANCE / HOLD / RECOVERY based on layer movement.

    Simple heuristic:
    - If blocker changed to a higher layer → ADVANCE
    - If same blocker but scores improved → HOLD
    - If same or worse blocker → RECOVERY (after 2 failures, but we simplify to score-based)
    """
    # Map layer to progression order
    order = {"STATE": 0, "CLARITY": 1, "EASE": 2, "TRUST": 3, "MOMENTUM": 4, "AUTHORITY": 5}
    prev_rank = order.get(prev_blocker or "STATE", 0)
    new_rank = order.get(new_blocker, 0)

    if new_rank > prev_rank:
        return "ADVANCE"

    # Score-based movement within same blocker
    score_map = {
        "STATE": scores.state_score,
        "CLARITY": scores.clarity_score,
        "EASE": scores.ease_score,
        "TRUST": scores.trust_score,
        "MOMENTUM": scores.momentum_score,
        "AUTHORITY": scores.authority_score,
    }
    current_score = score_map.get(new_blocker, 5.0)

    if new_blocker == prev_blocker and current_score >= 5.0:
        return "HOLD"

    return "RECOVERY"
