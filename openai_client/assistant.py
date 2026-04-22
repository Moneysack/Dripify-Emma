"""
OpenAI Chat API wrapper — nutzt dein ChatGPT-Konto via API Key.
Kein Assistant / kein Custom GPT nötig.

Emmas System-Prompt + Gesprächshistorie werden pro Kontakt in Supabase
gespeichert und bei jedem Turn als Messages-Array mitgeschickt.
"""
from __future__ import annotations
import logging
from openai import OpenAI
from config import settings

log = logging.getLogger(__name__)

_client: OpenAI | None = None

# Emmas Basis-System-Prompt (aus emma_core.jsonl)
EMMA_SYSTEM_PROMPT = """Du bist Emma — ein zustandsbasiertes Entscheidungs- und Führungssystem für Verkaufsgespräche auf LinkedIn.

KERNPRINZIPIEN:
- Du bist KEIN Chatbot, KEIN Vertriebsassistent.
- Du steuerst Bewegung, nicht Antworten.
- Jede Interaktion hat genau EIN Ziel: Bewegung erzeugen.
- Du verfolgst genau EINEN Blocker pro Turn.
- Du stellst maximal EINE Frage ODER gibst EINEN klaren nächsten Schritt.
- Keine Mischinterventionen. Keine Mehrfachziele.

KOMMUNIKATION:
- Klar, menschlich, respektvoll. Kein Corporate-Speak.
- Maximal 3-4 Sätze pro Antwort.
- Natürliche Sprache — keine technischen Formulierungen.
- Du greifst den Nutzer nicht an, bewertest nicht, stellst keine Überlegenheit dar.

HARD RULES:
- Wenn kein klarer Blocker bestimmt — nur Klärungsfrage, keine inhaltliche Antwort.
- Wenn Gate aktiv (Trust/Ease/Momentum/Authority zu niedrig) — KEIN Pitch, KEINE Eskalation.
- Du folgst der [EMMA DECISION] Instruktion exakt.
- Antworte immer auf Deutsch, außer der Prospect schreibt auf Englisch."""


def get_or_create_thread(thread_id: str | None) -> str:
    """Für Kompatibilität — gibt thread_id zurück oder 'new'."""
    return thread_id or "new"


def run_turn(
    thread_id: str,
    prospect_message: str,
    emma_instruction: str,
    conversation_history: list[dict] | None = None,
) -> str:
    """
    Generiert Emmas Antwort via OpenAI Chat API.

    conversation_history: Liste von {"role": "user"/"assistant", "content": "..."}
    """
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)

    messages = [{"role": "system", "content": EMMA_SYSTEM_PROMPT}]

    # Gesprächshistorie anhängen (max. letzte 10 Turns für Context-Limit)
    if conversation_history:
        messages.extend(conversation_history[-20:])

    # Emma-Entscheidungs-Instruktion als System-Message
    messages.append({
        "role": "system",
        "content": emma_instruction,
    })

    # Aktuelle Prospect-Nachricht
    messages.append({"role": "user", "content": prospect_message})

    response = _client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=300,
    )

    reply = response.choices[0].message.content.strip()
    log.debug("Emma reply (%d chars): %s...", len(reply), reply[:80])
    return reply
