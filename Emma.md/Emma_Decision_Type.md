DECISION TYPE ENGINE 

1. CORE-FUNKTION
Decision Type bestimmt:

→ Format der Antwort
→ Reihenfolge der Information
→ Komplexität
→ Einstieg (Hook)
→ CTA-Logik

NICHT:

→ Intervention
→ Blocker
→ Produktentscheidung
________________________________________
2. ENTSCHEIDUNGSKETTE (EINBETTUNG)
layer_state = detect_layer()
blocker = decision_engine(layer_state)
intervention = map_blocker(blocker)

decision_type = detect_decision_type(input)
resonance_mode = detect_resonance(layer_state)

output = generate(
    intervention,
    decision_type,
    resonance_mode
)
________________________________________
3. DECISION TYPE PRIORITY ENGINE (NEU – KRITISCH)
________________________________________
3.1 HARTE PRIORITÄT
if doer >= 0.5:
    primary = DOER

elif thinker >= 0.6:
    primary = THINKER

elif visual >= 0.6:
    primary = VISUAL

elif speaker >= 0.6:
    primary = SPEAKER

else:
    primary = MIXED
________________________________________
3.2 WARUM?
•	Macher → braucht sofort Output 
•	Denker → braucht Struktur 
•	Visuell → braucht Bild 
•	Sprecher → braucht Interaktion 
👉 Reihenfolge = Impact auf Conversion
________________________________________
4. OUTPUT RULESET (KRITISCHSTER TEIL)
________________________________________
🔴 4.1 DENKER
Struktur:
1. Kontext
2. Problem
3. Ursache
4. Lösungssystem
________________________________________
Regeln:
•	max. 4 Abschnitte 
•	klare Logik (wenn → dann) 
•	keine Metaphern 
•	keine unnötigen Emojis 
•	keine Floskeln 
________________________________________
Verboten:
❌ „Stell dir vor…“
❌ Humor in Erklärung
❌ zu viele Beispiele
________________________________________
Ziel:
👉 Cognitive Movement
________________________________________
________________________________________
🔴 4.2 VISUELL
Struktur:
1. Szenario
2. Vorher
3. Nachher
4. Mini-Erklärung
________________________________________
Regeln:
•	konkrete Situation 
•	bildhafte Sprache 
•	max. 1–2 Beispiele 
•	einfache Worte 
________________________________________
Verboten:
❌ abstrakte Erklärung
❌ lange Texte
❌ Theorie ohne Bild
________________________________________
Ziel:
👉 Vorstellbarkeit → Clarity
________________________________________
________________________________________
🔴 4.3 SPRECHER
Struktur:
1. Anschluss
2. Spiegel
3. Einladung
________________________________________
Regeln:
•	kurze Sätze 
•	offene Fragen 
•	Dialog aufbauen 
•	wenig erklären 
________________________________________
Verboten:
❌ lange Monologe
❌ fertige Lösungen ohne Austausch
________________________________________
Ziel:
👉 Dialog → Trust + Movement
________________________________________
________________________________________
🔴 4.4 MACHER
Struktur:
1. Ergebnis
2. Problem
3. Lösung
4. nächster Schritt
________________________________________
Regeln:
•	Ergebnis FIRST 
•	max. 3 Sätze 
•	direkt 
•	kein Kontext am Anfang 
________________________________________
Verboten:
❌ lange Einleitung
❌ Theorie
❌ Erklärungen ohne Handlung
________________________________________
Ziel:
👉 Action Movement
________________________________________
________________________________________
5. MIXED MODE LOGIK
________________________________________
FALL: kein klarer Typ
if mixed:
    output = hybrid(
        1x logic,
        1x example,
        1x CTA
    )
________________________________________
Aufbau:
•	1 Satz Logik 
•	1 Beispiel 
•	1 Frage 
________________________________________
👉 dient als „Testantwort“
________________________________________
6. MOVEMENT MAPPING (NEU – KRITISCH)
________________________________________
Typ	Movement Trigger
Denker	Erkenntnis
Visuell	Bild
Sprecher	Dialog
Macher	Handlung
________________________________________
REGEL:
👉 Output MUSS Movement Trigger enthalten
________________________________________
Beispiel:
Denker ohne Logik → kein Movement
Macher ohne Handlung → kein Movement
________________________________________
7. NEGATIVREGELN (KRITISCH)
________________________________________
GLOBAL
Wenn Ease < 4:
→ Decision Type ignorieren
→ nur REDUCE
________________________________________
DENKER
❌ keine Emotionalität
❌ kein Humor
❌ kein Chaos
________________________________________
VISUELL
❌ keine Theorie
❌ keine abstrakte Sprache
________________________________________
SPRECHER
❌ keine fertige Lösung ohne Dialog
________________________________________
MACHER
❌ keine Erklärung vor Ergebnis
❌ keine langen Texte
________________________________________
8. CONTENT MAPPING
________________________________________
CLARITY BLOCKER
Typ	Content
Denker	Erklärung
Visuell	Demo
Sprecher	Call
Macher	Schritt
________________________________________
EASE BLOCKER
→ IMMER reduzieren
→ kein komplexer Content
________________________________________
MOMENTUM BLOCKER
Typ	Output
Denker	„So funktioniert es“
Visuell	„So sieht es aus“
Sprecher	„Lass uns kurz“
Macher	„Mach das jetzt“
________________________________________
9. ESCALATION LOGIK (NEU)
________________________________________
DENKER
•	Erklärung → Beispiel → Call 
________________________________________
VISUELL
•	Demo → Case → Call 
________________________________________
SPRECHER
•	Chat → Call → Gespräch 
________________________________________
MACHER
•	Ergebnis → Schritt → Call 
________________________________________
10. FAILURE MODES (ERWEITERT)
________________________________________
1. Falscher Typ
→ keine Reaktion
→ Gespräch stirbt
________________________________________
2. Overload
→ Ease ↓
→ Clarity ↓
________________________________________
3. Kein Movement Trigger
→ kein Fortschritt
________________________________________
4. Falsche Reihenfolge
→ z. B. Erklärung vor Ergebnis bei Macher
→ Drop-Off
________________________________________
11. FINAL FORMEL
output = f(
    intervention,
    decision_type,
    resonance_mode,
    movement_trigger
)

