"""
Signal detection: reads a prospect's message and returns layer deltas.

Each signal pattern is (regex, layer, score_delta, confidence_delta).
Patterns are matched case-insensitively. Multiple patterns can fire per message.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from emma.layers import LayerScores

@dataclass
class Signal:
    layer: str
    score_delta: float
    confidence_delta: float = 0.0
    description: str = ""


# ─── Signal definitions ───────────────────────────────────────────────────────
# Format: (pattern, layer, delta, confidence_delta, description)
SIGNAL_PATTERNS: list[tuple[str, str, float, float, str]] = [

    # ── TRUST signals ─────────────────────────────────────────────────────────
    (r"bin (etwas |sehr |eher )?(vorsichtig|skeptisch|zurückhaltend)", "TRUST", -1.5, 0.1, "trust_skeptic"),
    (r"klingt (wie|nach) (werbung|verkauf|pitch|spam)", "TRUST", -2.0, 0.1, "trust_sales_suspect"),
    (r"schon (oft|viele) (solche|ähnliche) (angebote|nachrichten)", "TRUST", -1.5, 0.1, "trust_prior_negative"),
    (r"(warum|weshalb) schreibst du mir", "TRUST", -1.0, 0.0, "trust_suspicious"),
    (r"(wer bist du|was willst du|was verkaufst du)", "TRUST", -1.5, 0.1, "trust_identity_challenge"),
    (r"(kenn(e|t) dich nicht|keine (beziehung|verbindung))", "TRUST", -1.0, 0.0, "trust_no_relation"),
    (r"(interessant|klingt gut|gerne mehr)", "TRUST", +1.0, 0.0, "trust_open"),
    (r"(danke|freue mich|gern(e)?)", "TRUST", +0.5, 0.0, "trust_positive"),

    # ── EASE signals ──────────────────────────────────────────────────────────
    (r"(gerade |zurzeit |aktuell )?(viel |sehr viel )?(los|beschäftigt|busy|stress)", "EASE", -2.0, 0.0, "ease_overwhelmed"),
    (r"(keine|wenig|kaum) (zeit|kapazität|ressourcen)", "EASE", -1.5, 0.0, "ease_no_time"),
    (r"(bin (gerade )?im urlaub|on vacation)", "EASE", -2.0, 0.0, "ease_vacation"),
    (r"(zu viel|überfordert|overwhelmed)", "EASE", -2.0, 0.0, "ease_overload"),
    (r"(kurz|schnell|in kürze|brief)", "EASE", +0.5, 0.0, "ease_receptive"),
    (r"(bin offen|schick mir|gerne|ja klar)", "EASE", +1.0, 0.0, "ease_open"),

    # ── MOMENTUM signals ──────────────────────────────────────────────────────
    (r"(machen wir|lass uns|können wir starten|wann können wir)", "MOMENTUM", +2.0, 0.0, "momentum_intent"),
    (r"(schick (mal|mir)|send (me|mal)|zeig mir)", "MOMENTUM", +1.5, 0.0, "momentum_request"),
    (r"(wann|wie schnell|how soon)", "MOMENTUM", +1.0, 0.0, "momentum_timeline"),
    (r"(kein (bedarf|interesse|thema)|not interested|no need)", "MOMENTUM", -2.5, 0.0, "momentum_rejection"),
    (r"(vielleicht|maybe|irgendwann|sometime|später|later)", "MOMENTUM", -1.0, 0.0, "momentum_delay"),
    (r"(macht sinn|ergibt sinn|logisch|sounds good|verstehe)", "MOMENTUM", +1.0, 0.0, "momentum_cognitive"),

    # ── AUTHORITY signals ─────────────────────────────────────────────────────
    (r"(muss (das|es) (erst |noch )?(ab)?klären|muss das intern besprechen)", "AUTHORITY", -2.0, 0.2, "authority_dependency"),
    (r"(entscheide(t)? (das )?(nicht )?allein(e)?|entscheiden (wir |das )?gemeinsam)", "AUTHORITY", -1.5, 0.1, "authority_collective"),
    (r"(das entscheide(t)? (jemand anders|mein chef|meine führung|mein vorgesetzter))", "AUTHORITY", -3.0, 0.2, "authority_not_decider"),
    (r"(ich entscheide (das|es) (selbst|allein(e)?)|bin (der|die) (entscheider|ceo|gf|geschäftsführer))", "AUTHORITY", +3.0, 0.1, "authority_decider"),
    (r"(ich (kann|könnte) (das|es) anstoßen|kann ich weiterleiten)", "AUTHORITY", +1.0, 0.0, "authority_limited_control"),
    (r"(ich (hole|bringe|nehme) (jemanden|meinen|meine) dazu)", "AUTHORITY", +2.0, 0.0, "authority_route"),
    (r"(kläre (das |es )?(intern|kurz)|schau (mal|kurz) rein)", "AUTHORITY", 0.0, -0.1, "authority_fake"),

    # ── STATE signals (problem awareness) ─────────────────────────────────────
    (r"(stimmt|das ist tatsächlich|da hast du recht|ja, (das|das ist))", "STATE", +1.0, 0.0, "state_recognition"),
    (r"(problem|herausforderung|schwierigkeit|issue|challenge)", "STATE", +1.5, 0.0, "state_problem_aware"),
    (r"(kein problem|alles gut|läuft gut|no issues|everything's fine)", "STATE", -0.5, 0.0, "state_denial"),
    (r"(dann (hätten|wären) wir|das (wäre|würde) (schon|tatsächlich))", "STATE", +2.0, 0.0, "state_scenario_accept"),

    # ── CLARITY signals ───────────────────────────────────────────────────────
    (r"(verstehe (das |es )?(noch )?nicht|unklar|was meinst du|was bedeutet das)", "CLARITY", -1.5, 0.0, "clarity_confused"),
    (r"(konkret|genau|spezifisch|zum beispiel|for example)", "CLARITY", +1.0, 0.0, "clarity_seeking"),
    (r"(dann würde(n)? (ich|wir|es)|das bedeutet (für mich|für uns))", "CLARITY", +2.0, 0.0, "clarity_translation"),
    (r"(ah|aha|verstehe jetzt|macht sinn jetzt|now i get it)", "CLARITY", +1.5, 0.0, "clarity_aha"),

    # ── DECISION TYPE signals ──────────────────────────────────────────────────
    (r"(wie funktioniert|wie genau|welche daten|welche logik|warum)", "STATE", +0.0, 0.0, "type_thinker_hint"),  # handled separately below
    (r"(was kostet|was bringt|ergebnis|outcome|roi|rendite)", "STATE", +0.0, 0.0, "type_doer_hint"),
    (r"(stell dir vor|wie würde das aussehen|zeig mir|demo)", "STATE", +0.0, 0.0, "type_visual_hint"),
    (r"(reden wir|lass uns sprechen|können wir kurz?|call)", "STATE", +0.0, 0.0, "type_speaker_hint"),
]

# Decision type detection patterns (separate from layer scoring)
_TYPE_PATTERNS = [
    (r"(wie funktioniert|wie genau|welche daten|welche logik|warum|analyse|struktur)", "THINKER"),
    (r"(was kostet|was bringt|ergebnis|outcome|roi|rendite|action|mach|direkt)", "DOER"),
    (r"(stell dir vor|wie würde das aussehen|zeig mir|demo|bild|beispiel)", "VISUAL"),
    (r"(reden wir|lass uns sprechen|können wir kurz|call|chat)", "SPEAKER"),
]


def detect_signals(text: str) -> list[Signal]:
    """Return all signals fired by the prospect's message."""
    signals: list[Signal] = []
    lower = text.lower()

    for pattern, layer, delta, conf_delta, description in SIGNAL_PATTERNS:
        if delta == 0.0 and conf_delta == 0.0:
            continue  # type-hint rows — handled by detect_decision_type
        if re.search(pattern, lower):
            signals.append(Signal(layer=layer, score_delta=delta, confidence_delta=conf_delta, description=description))

    return signals


def detect_decision_type(text: str) -> str | None:
    """Return dominant decision type if detectable, else None."""
    lower = text.lower()
    counts: dict[str, int] = {}
    for pattern, dtype in _TYPE_PATTERNS:
        if re.search(pattern, lower):
            counts[dtype] = counts.get(dtype, 0) + 1
    if not counts:
        return None
    return max(counts, key=lambda k: counts[k])


def apply_signals(scores: LayerScores, signals: list[Signal]) -> LayerScores:
    for sig in signals:
        scores.apply_delta(sig.layer, sig.score_delta, sig.confidence_delta)
    scores.cascade()
    return scores
