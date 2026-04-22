"""Layer score definitions and clamping helpers."""
from __future__ import annotations
from dataclasses import dataclass

# Gate thresholds — from Conversation Flow JSONL section 6
TRUST_GATE = 5.0
EASE_GATE = 4.0
MOMENTUM_GATE = 4.0
AUTHORITY_GATE = 5.0

SCORE_MIN = 0.0
SCORE_MAX = 10.0
CONFIDENCE_MIN = 0.0
CONFIDENCE_MAX = 1.0


def clamp(value: float, lo: float = SCORE_MIN, hi: float = SCORE_MAX) -> float:
    return max(lo, min(hi, value))


@dataclass
class LayerScores:
    """Mirrors the emma_state DB row for in-memory computation."""
    state_score: float = 5.0
    clarity_score: float = 5.0
    ease_score: float = 5.0
    trust_score: float = 5.0
    momentum_score: float = 5.0
    authority_score: float = 5.0
    authority_confidence: float = 0.5
    decision_type: str = "MIXED"

    def apply_delta(self, layer: str, delta: float, confidence_delta: float = 0.0):
        """Update a single layer score and optionally its confidence."""
        if layer == "STATE":
            self.state_score = clamp(self.state_score + delta)
        elif layer == "CLARITY":
            self.clarity_score = clamp(self.clarity_score + delta)
        elif layer == "EASE":
            self.ease_score = clamp(self.ease_score + delta)
        elif layer == "TRUST":
            self.trust_score = clamp(self.trust_score + delta)
        elif layer == "MOMENTUM":
            self.momentum_score = clamp(self.momentum_score + delta)
        elif layer == "AUTHORITY":
            self.authority_score = clamp(self.authority_score + delta)
            self.authority_confidence = clamp(
                self.authority_confidence + confidence_delta,
                CONFIDENCE_MIN, CONFIDENCE_MAX,
            )

    def cascade(self):
        """Apply cascade logic: Trust↓ → Momentum↓ → Ease↓ (secondary effects)."""
        if self.trust_score < TRUST_GATE:
            self.momentum_score = clamp(self.momentum_score - 0.5)
            self.ease_score = clamp(self.ease_score - 0.3)

    def to_dict(self) -> dict:
        return {
            "state": round(self.state_score, 2),
            "clarity": round(self.clarity_score, 2),
            "ease": round(self.ease_score, 2),
            "trust": round(self.trust_score, 2),
            "momentum": round(self.momentum_score, 2),
            "authority": round(self.authority_score, 2),
            "authority_confidence": round(self.authority_confidence, 2),
            "decision_type": self.decision_type,
        }
