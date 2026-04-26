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


# Human-readable instruction snippets injected into the OpenAI system prompt per turn
INTERVENTION_INSTRUCTIONS: dict[str, str] = {
    "MIRROR": (
        "MIRROR — Goal: reflect their reality without judgment.\n"
        "Do NOT offer a solution. Do NOT pitch. Do NOT explain.\n"
        "1–2 sentences that show you heard them, then one open question that opens their thinking.\n"
        "Example feel: 'Versteh ich. Die meisten merken das erst, wenn es anfängt, sie wirklich zu nerven. "
        "Was passiert bei euch, wenn jemand plötzlich ausfällt?'"
    ),
    "REFRAME": (
        "REFRAME — Goal: open a new perspective on the problem.\n"
        "Do NOT explain, do NOT convince, do NOT offer a solution yet.\n"
        "Introduce one structural thought: what happens if the problem stays?\n"
        "End with exactly one question that makes them reconsider. No pitch."
    ),
    "SAFETY": (
        "SAFETY — Goal: increase perceived safety and lower threat level.\n"
        "No evaluation, no argumentation, no persuasion, no justification, no humor.\n"
        "Validate the skepticism explicitly. Ask one soft, open question about the specific concern.\n"
        "Do NOT say 'Ich helfe dir', 'unsere Lösung', or any claim/promise.\n"
        "Tone: calm, patient, zero pressure."
    ),
    "TRUST_BUILD": (
        "TRUST_BUILD — Goal: build credibility gradually.\n"
        "Validate their experience first. Then share one concrete, transparent fact or example.\n"
        "No exaggeration, no big claims. One quiet question at the end.\n"
        "No escalation. No product mention."
    ),
    "CLARIFY": (
        "CLARIFY — Goal: remove uncertainty without leading the answer.\n"
        "Ask exactly one open, neutral question. Do NOT interpret. Do NOT suggest a direction.\n"
        "If they said 'makes sense / sounds logical' without real understanding: do NOT agree and continue. "
        "Ask one concretizing question instead: 'Was würde das konkret für euch bedeuten?'"
    ),
    "STRUCTURE": (
        "STRUCTURE — Goal: make one concept clear and tangible.\n"
        "Use a simple if→then logic. Maximum 3 points. No options, no overload.\n"
        "Speak in everyday language, not abstract concepts.\n"
        "For THINKER type: cause→effect allowed. For others: keep it visual and concrete.\n"
        "End with one question."
    ),
    "REDUCE": (
        "REDUCE — Goal: remove all friction and cognitive load.\n"
        "MAXIMUM: one thought + one question. Response must be 1–2 lines only.\n"
        "No content, no explanation, no solution, no pitch, no complexity.\n"
        "Acknowledge their capacity constraint, give them space.\n"
        "Example: 'Macht Sinn. Magst du mir kurz sagen, was gerade das Größte ist?'"
    ),
    "ACTIVATE": (
        "ACTIVATE — Goal: trigger one small, concrete next action.\n"
        "Do NOT explain more. Do NOT pitch again. They already agreed or showed interest.\n"
        "Name one mini-step that requires minimal commitment.\n"
        "Direct, brief, action-oriented. No big ask."
    ),
    "ROUTE": (
        "ROUTE — Goal: clarify the decision path, not the content.\n"
        "Do NOT add more content or benefits. Focus only on: who decides, how does the process work, "
        "what does the next internal step look like?\n"
        "No closing attempt. No pitch. Just structure the path forward."
    ),
    "PARK": (
        "PARK — Goal: deliberately slow the conversation. Respect their current state.\n"
        "Leave one open, inviting door with zero pressure.\n"
        "Short, warm, no content. Let them come back on their terms."
    ),
}


def get_intervention_instruction(intervention: str) -> str:
    return INTERVENTION_INSTRUCTIONS.get(intervention, "Reagiere empathisch und stelle eine klare Frage.")
