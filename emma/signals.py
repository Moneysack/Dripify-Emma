"""
Signal detection — translates prospect messages into layer score deltas.

Signal types per Emma documentation:
  Critical signals  → immediate override, set layer as dominant blocker
  Strong signals    → ±2 to ±3
  Weak signals      → ±0.5 to ±1

Gate thresholds (from Decision Engine):
  Trust < 5, Ease < 4, Momentum < 4, Authority < 5
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
    is_critical: bool = False


# ─── Signal definitions ───────────────────────────────────────────────────────
# (pattern, layer, delta, conf_delta, description, is_critical)
SIGNAL_PATTERNS: list[tuple[str, str, float, float, str, bool]] = [

    # ══ TRUST signals ═════════════════════════════════════════════════════════
    # Critical negative — immediate trust blocker
    (r"(klingt (wie|nach) (werbung|verkauf|pitch|spam|cold ?call))", "TRUST", -2.5, 0.2, "trust_sales_suspect", True),
    (r"(sowas (kenn|hab) ich|hab (schon|schon oft) (solche?|ähnliche?) (nachrichten?|angebote?|anfragen?))", "TRUST", -2.0, 0.2, "trust_prior_negative", True),
    (r"(was willst du (von mir)?|was verkaufst du|was ist das (hier|genau))", "TRUST", -2.0, 0.15, "trust_intent_challenge", True),

    # Strong negative
    (r"(bin (etwas|sehr|eher|ziemlich) (vorsichtig|skeptisch|zurückhaltend|misstrauisch))", "TRUST", -2.0, 0.1, "trust_skeptic", False),
    (r"(warum schreibst? du mir|wer bist du|kenne? dich nicht|keine (verbindung|beziehung|ahnung wer du bist))", "TRUST", -1.5, 0.1, "trust_no_relation", False),
    (r"(nicht sicher ob|bin vorsichtig bei|glaube (das|ich) nicht so recht)", "TRUST", -1.5, 0.1, "trust_doubt", False),

    # Weak negative
    (r"(mal schauen|erst (mal|abwarten)|abwarten)", "TRUST", -0.5, 0.0, "trust_wait_see", False),

    # Positive
    (r"(interessant|klingt (gut|spannend|interessant)|gerne (mehr|dazu|hören))", "TRUST", +1.0, 0.0, "trust_open", False),
    (r"(danke (für|dass)|freue mich|sehr gerne|stimmt so)", "TRUST", +0.5, 0.0, "trust_positive", False),
    (r"(ja (klar|natürlich|gerne)|sehr (interessant|relevant)|genau (mein|das) (thema|problem))", "TRUST", +1.5, 0.0, "trust_strong_open", False),
    (r"(hab (schon|bereits) (von dir|über dich|euch) gehört|kenne (dich|euch|das))", "TRUST", +2.0, 0.1, "trust_prior_positive", False),

    # ══ EASE signals ══════════════════════════════════════════════════════════
    # Critical overload — immediate ease blocker
    (r"(habe? keinen (kopf|platz|raum) (dafür|für das)|schaffe? das nicht (auch )?noch)", "EASE", -3.0, 0.2, "ease_overload_critical", True),
    (r"(gerade (total|komplett|absolut) (überlastet|überfordert|im stress|dicht))", "EASE", -2.5, 0.2, "ease_overload_critical2", True),

    # Strong negative
    (r"(gerade |zurzeit |aktuell )?(viel |sehr viel |zu viel )?(los|beschäftigt|busy|stress|druck)", "EASE", -2.0, 0.1, "ease_overwhelmed", False),
    (r"(keine |wenig |kaum )(zeit|kapazität|ressourcen|energie|nerven)", "EASE", -2.0, 0.1, "ease_no_capacity", False),
    (r"(bin (gerade )?im urlaub|reise gerade|on vacation|außer haus)", "EASE", -2.0, 0.1, "ease_away", False),
    (r"(zu viel|überlastet|overwhelmed|zu viele baustellen|zu viele projekte)", "EASE", -2.0, 0.1, "ease_too_much", False),

    # Moderate negative
    (r"(vielleicht (später|nochmal)|mal schauen|später (nochmal|vielleicht)|kommt drauf an)", "EASE", -1.5, 0.0, "ease_resistance", False),
    (r"(nicht (der|die) (beste|richtige) (zeitpunkt|moment|phase))", "EASE", -1.5, 0.1, "ease_bad_timing", False),

    # Positive
    (r"(klingt (einfach|unkompliziert|simpel)|wenn das (einfacher|schneller|weniger aufwand) (geht|ist))", "EASE", +2.5, 0.1, "ease_relief_hook", False),
    (r"(will (weniger|einfach weniger)|einfach (mehr |weniger )?(ruhe|ordnung|klarheit|chaos))", "EASE", +2.0, 0.1, "ease_relief_seek", False),
    (r"(bin offen|schick (mal|mir)|gerne|ja klar|kein problem|passt)", "EASE", +1.5, 0.0, "ease_open", False),
    (r"(lass uns (das )?machen|lass uns starten|fangen wir an)", "EASE", +2.5, 0.1, "ease_action_energy", False),
    (r"(kurz |schnell |in kürze|short)", "EASE", +0.5, 0.0, "ease_receptive", False),

    # ══ MOMENTUM signals ══════════════════════════════════════════════════════
    # Strong positive
    (r"(machen wir|lass uns (das )?angehen|können wir starten|wann (können|starten) wir)", "MOMENTUM", +2.5, 0.1, "momentum_intent_strong", False),
    (r"(ich will das (jetzt|sofort|direkt) angehen|lass uns das fixieren)", "MOMENTUM", +3.0, 0.1, "momentum_action", False),
    (r"(wann (kann|können|habt ihr)|wie schnell|how soon|wann (ist|wäre) das (möglich|machbar))", "MOMENTUM", +2.0, 0.0, "momentum_timeline", False),
    (r"(schick (mal|mir)|send (me|mal)|zeig mir (mal)?|kannst du mir schicken)", "MOMENTUM", +1.5, 0.0, "momentum_request", False),

    # Moderate positive
    (r"(macht sinn|ergibt sinn|logisch|sounds good|das (leuchtet|sehe ich)|verstehe (den punkt|warum))", "MOMENTUM", +1.0, 0.0, "momentum_cognitive", False),
    (r"(klingt (gut|sinnvoll|interessant) — ?lass uns)", "MOMENTUM", +1.5, 0.0, "momentum_positive_lean", False),

    # Negative
    (r"(kein (bedarf|interesse|thema|handlungsbedarf)|not interested|no need|brauchen wir (gerade )?nicht)", "MOMENTUM", -2.5, 0.1, "momentum_rejection", False),
    (r"(vielleicht (später|mal)|maybe|irgendwann|sometime|später|later|erstmal abwarten)", "MOMENTUM", -1.5, 0.0, "momentum_delay", False),
    (r"(läuft (gerade )?gut|haben (das )?schon|sind (schon )?versorgt|passt (gerade )?so)", "MOMENTUM", -1.0, 0.0, "momentum_satisfied", False),

    # ══ AUTHORITY signals ═════════════════════════════════════════════════════
    # Critical negative — not the decider
    (r"(das entscheide[tn]? (jemand anders|mein chef|meine (führung|chefin)|mein vorgesetzter|die geschäftsführung))", "AUTHORITY", -3.0, 0.3, "authority_not_decider", True),
    (r"(muss (das|es) (erst |noch )?(intern )?abklären|(muss|müssen) (das|es) besprechen)", "AUTHORITY", -2.0, 0.2, "authority_dependency", False),
    (r"(entscheid[ee]n? (wir |das )?gemeinsam|entscheide(t)? (das )?(nicht )?alleine?)", "AUTHORITY", -1.5, 0.1, "authority_collective", False),

    # Fake authority — no real movement
    (r"(kläre (das |es )?(intern|kurz)|schau (mal|kurz) rein|gebe (das |es )?weiter)", "AUTHORITY", 0.0, -0.2, "authority_fake", False),

    # Positive
    (r"(ich entscheide (das|es) (selbst|alleine?)|bin (der|die) (entscheider|ceo|gf|geschäftsführer|inhaber|founder))", "AUTHORITY", +3.0, 0.2, "authority_decider", False),
    (r"(ich (kann|könnte) (das|es) (direkt )?anstoßen|habe? (da(für)? )?budget)", "AUTHORITY", +1.5, 0.1, "authority_limited_control", False),
    (r"(ich (hole|bringe|nehme|ziehe) (jemanden?|meinen?|meine?) (dazu|rein|hinzu))", "AUTHORITY", +2.0, 0.1, "authority_route_positive", False),
    (r"(wir entscheiden (das)? (relativ )?schnell|kurze entscheidungswege|bin direkt zuständig)", "AUTHORITY", +2.0, 0.1, "authority_fast_decision", False),

    # ══ STATE signals (problem awareness) ════════════════════════════════════
    # Strong recognition
    (r"(stimmt(,| —| —)? (das|eigentlich|tatsächlich)|da hast du (recht|einen punkt)|ja, (das ist|das stimmt))", "STATE", +2.0, 0.0, "state_recognition_strong", False),
    (r"(tatsächlich (ein |unser )?(problem|thema|herausforderung)|kämpfen (damit|da(gegen|mit)) (schon|gerade|ständig))", "STATE", +2.5, 0.1, "state_problem_confirmed", False),
    (r"(dann (hätten|wären|würden) wir|das (wäre|würde) (schon|tatsächlich|definitiv))", "STATE", +2.0, 0.0, "state_scenario_accept", False),

    # Moderate recognition
    (r"(problem|herausforderung|schwierigkeit|issue|challenge|engpass|flaschenhals)", "STATE", +1.5, 0.0, "state_problem_aware", False),
    (r"(nervt (mich|uns)|macht (mir|uns) zu schaffen|schon öfter aufgefallen|passiert (ständig|immer wieder))", "STATE", +1.5, 0.0, "state_frustration", False),

    # Weak / denial
    (r"(kein problem|alles (gut|okay|top|super)|läuft gut|no issues|everything'?s? fine)", "STATE", -0.5, 0.0, "state_denial", False),
    (r"(nicht wirklich|eigentlich nicht|so schlimm (ist|war) das nicht)", "STATE", -1.0, 0.0, "state_minimization", False),

    # ══ CLARITY signals ═══════════════════════════════════════════════════════
    # Strong confusion — critical
    (r"(verstehe (das |es |das alles )?(nicht|noch nicht|immer noch nicht)|ergibt keinen sinn|macht keinen sinn)", "CLARITY", -2.5, 0.1, "clarity_confused_strong", True),
    (r"(was meinst du (damit|genau)|was bedeutet das (für mich|konkret)|wie genau (meinst|funktioniert) das)", "CLARITY", -2.0, 0.1, "clarity_confused", False),

    # Fake clarity
    (r"(klingt logisch|macht sinn|verstehe ich|ja (sicher|klar)|okay, gut)", "CLARITY", +0.5, -0.1, "clarity_fake", False),

    # Concrete translation — strong positive
    (r"(dann würde(n)? (ich|wir|das|es)|das bedeutet (für mich|für uns|konkret))", "CLARITY", +2.5, 0.1, "clarity_translation", False),
    (r"(also (grob|vereinfacht|konkret) heißt das|dann (könnte|würde) (mein|unser))", "CLARITY", +2.0, 0.1, "clarity_partial_translation", False),
    (r"(ah(a)?[,!]|jetzt (verstehe|sehe|kapiere) ich|now i get it|das leuchtet (mir )?ein)", "CLARITY", +2.0, 0.0, "clarity_aha", False),

    # Next step clarity
    (r"(was wäre (der|ein) (erste[rn]?|nächste[rn]?) schritt|wie (setze|fange) ich das (konkret )?(um|an))", "CLARITY", +2.0, 0.0, "clarity_next_step", False),
]


# Decision type detection patterns
_TYPE_PATTERNS = [
    (r"(wie funktioniert|wie genau|welche daten|welche logik|warum|analyse|struktur|zeig mir die zahlen|belege)", "THINKER"),
    (r"(was kostet|was bringt|ergebnis|outcome|roi|rendite|action|mach|direkt|einfach machen|konkretes ergebnis)", "DOER"),
    (r"(stell dir vor|wie würde das aussehen|zeig mir|demo|bild|beispiel|kannst du zeigen)", "VISUAL"),
    (r"(reden wir|lass uns sprechen|können wir kurz|call|chat|telefonieren|video)", "SPEAKER"),
]


def detect_signals(text: str) -> list[Signal]:
    """Return all signals fired by the prospect's message."""
    signals: list[Signal] = []
    lower = text.lower()

    for pattern, layer, delta, conf_delta, description, is_critical in SIGNAL_PATTERNS:
        if re.search(pattern, lower):
            signals.append(Signal(
                layer=layer,
                score_delta=delta,
                confidence_delta=conf_delta,
                description=description,
                is_critical=is_critical,
            ))

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
    """Apply all signals; critical signals override layer score immediately."""
    # Apply critical signals first
    for sig in signals:
        if sig.is_critical:
            scores.apply_delta(sig.layer, sig.score_delta, sig.confidence_delta)
    # Then apply remaining signals
    for sig in signals:
        if not sig.is_critical:
            scores.apply_delta(sig.layer, sig.score_delta, sig.confidence_delta)
    scores.cascade()
    return scores
