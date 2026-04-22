"""
Maps (blocker, layer scores, flow_mode) → exactly one intervention.

Interventions from JSONL files:
  MIRROR, REFRAME, SAFETY, TRUST_BUILD, CLARIFY, REDUCE,
  STRUCTURE, ACTIVATE, ROUTE, PARK
"""
from __future__ import annotations
from emma.layers import LayerScores


def map_intervention(blocker: str, scores: LayerScores, flow_mode: str = "HOLD") -> str:
    """Return the single intervention Emma should use this turn."""

    if blocker == "STATE":
        # Mirror first, then reframe once some state movement exists
        if scores.state_score < 4.0:
            return "MIRROR"
        return "REFRAME"

    if blocker == "CLARITY":
        if scores.clarity_score < 4.0:
            return "CLARIFY"
        return "STRUCTURE"

    if blocker == "EASE":
        # Always reduce — no other intervention allowed when Ease gate is active
        return "REDUCE"

    if blocker == "TRUST":
        if scores.trust_score < 4.0:
            return "SAFETY"
        return "TRUST_BUILD"

    if blocker == "MOMENTUM":
        # RECOVERY mode → don't push, just reduce or mirror
        if flow_mode == "RECOVERY":
            return "REDUCE"
        return "ACTIVATE"

    if blocker == "AUTHORITY":
        if scores.authority_score < 4.0:
            return "ROUTE"
        return "ROUTE"  # soft route — clarify decision path

    return "MIRROR"  # fallback


# Human-readable instruction snippets injected into the OpenAI system prompt
INTERVENTION_INSTRUCTIONS: dict[str, str] = {
    "MIRROR": (
        "Spiegele den Zustand des Nutzers zurück. Keine Lösung, kein Pitch. "
        "Maximal 2 Sätze + eine offene Frage."
    ),
    "REFRAME": (
        "Reframe das Problem auf die strukturelle Ebene. "
        "Konkrete Frage: Was passiert, wenn das Problem bleibt?"
    ),
    "SAFETY": (
        "Baue Sicherheit auf. Kein Druck, kein Pitch, kein Humor. "
        "Validiere die Skepsis, frage konkret nach dem Bedenken."
    ),
    "TRUST_BUILD": (
        "Öffne vorsichtig. Validiere die Erfahrung, gib etwas Konkretes preis. "
        "Keine Eskalation. Eine ruhige Frage."
    ),
    "CLARIFY": (
        "Stelle eine einfache, konkrete Klärungsfrage. "
        "Kein Erklären. Reduktion auf das Wesentlichste."
    ),
    "STRUCTURE": (
        "Gib dem Nutzer eine klare, logische Struktur (wenn → dann). "
        "Max. 3 Punkte. Keine Optionen, kein Overload."
    ),
    "REDUCE": (
        "Maximal EINEN Gedanken + EINE Frage. Kein Erklären, keine Lösung, kein Pitch. "
        "Druck rausnehmen, Raum geben."
    ),
    "ACTIVATE": (
        "Aktiviere den nächsten konkreten Schritt. Kurz, direkt, handlungsorientiert. "
        "Nenn einen mini-Schritt, keine große Verpflichtung."
    ),
    "ROUTE": (
        "Klär den Entscheidungspfad. Wer entscheidet das? Wie läuft das intern ab? "
        "Kein Closing, kein Nutzen-Pitch. Nur Struktur."
    ),
    "PARK": (
        "Verlangsame das Gespräch bewusst. Respektiere den Zustand. "
        "Hinterlasse eine einladende, offene Tür ohne Druck."
    ),
}


def get_intervention_instruction(intervention: str) -> str:
    return INTERVENTION_INSTRUCTIONS.get(intervention, "Reagiere empathisch und stelle eine klare Frage.")
