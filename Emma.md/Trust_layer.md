1. CORE-FRAGE
Fühlt sich die Person sicher genug, um offen zu sein und sich auf den nächsten Schritt einzulassen?
 
2. DEFINITION
TRUST misst das wahrgenommene Sicherheits- und Glaubwürdigkeitsniveau.
 
Nicht:
→ Sympathie
→ Interesse
 
Sondern:
→ Erwartung an Risiko vs. Sicherheit
→ Schutzmechanismen
→ Bereitschaft, sich einzulassen
→ Angst vor Wiederholung negativer Erfahrungen
 
3. SCORE SYSTEM
trust_score: 0–10
trust_confidence: 0–1
 
4. SCORE INTERPRETATION
Score​​​​​Zustand​​​​Bedeutung
0–2​​​​​Abwehr​​​​aktives Misstrauen
3–4​​​​​defensiv​​​​Schutz aktiv
5–6​​​​​neutral​​​​vorsichtig offen
7–8​​​​​offen​​​​​Vertrauen wächst
9–10​​​​​committed​​​​hohe Sicherheit
5. SIGNAL-EINHEIT
Ein Signal ist eine semantisch abgeschlossene Aussage mit Bezug auf:
→ Sicherheit
→ Zweifel
→ Erfahrung
→ Erwartung
→ Risiko
 
Eine Nachricht kann mehrere Signale enthalten.
 
6. SIGNALTYPEN
6.1 Skepsis-Signal
Zweifel ohne konkrete Erfahrung
Beispiele:
„Das sagen viele“
„Klingt gut, aber…“

→ Wirkung: -1 bis -2
 
6.2 Erfahrungs-Signal (NEU GESCHÄRFT)
 
Basierend auf Vergangenheit – MUSS klassifiziert werden:
 
negativ-resigniert
→ Vertrauen gesunken, Schutz hoch
„Ich habe alles probiert, bringt eh nichts“
→ -2 bis -3
 
neutral-reflektiert
→ Erfahrung ohne Schutz
„Ich habe schon einiges probiert“
→ 0
 
offen-lernend
→ Erfahrung + Bereitschaft
„Ich habe viel probiert, aber vielleicht falsch“
→ +1
 
6.3 Schutz-Signal
aktive Distanz / Selbstschutz
Beispiele:
„Ich bin da vorsichtig“
„Ich will nichts überstürzen“
→ -1 bis -2
→ erhöht Reibung
 
6.4 Vertrauens-Signal
 
positive Resonanz
Beispiele:
„Macht Sinn“
„Das klingt fair“
→ +1 bis +2
 
6.5 Commit-Signal
Handlungsbereitschaft
Beispiele:
„Wie geht’s weiter?“
„Was ist der nächste Schritt?“
→ +2 bis +3
 
6.6 KRITISCHES SIGNAL
→ sofortiger Override
Beispiele:
„Ich habe schlechte Erfahrungen gemacht“
„Ich wurde schon mal abgezogen“
„Ich glaube sowas grundsätzlich nicht“
 
KRITISCHE REGEL
→ trust_score ≤ 3
→ trust_confidence ↑
→ CRITICAL MODE aktiv
→ sofortiger Logikwechsel
 
7. SIGNALVERARBEITUNG
trust_score += signal_delta
trust_confidence += confidence_delta
 
Regeln:
schwach: ±1
stark: ±2–3
kritisch: Override

8. MEMORY-LOGIK
Trust ist hoch persistent.
Regeln:
negative Signale wirken länger als positive
Vertrauen steigt langsam
Vertrauen fällt schnell
mehrere positive Signale nötig für echten Anstieg

9. MOVEMENT IMPACT (NEU)

Trust blockiert Bewegung auf drei Ebenen:
1. Offenheit
→ Nutzer sagt nicht die Wahrheit
2. Verarbeitung
→ Nutzer nimmt Input nicht an
 
3. Entscheidung
→ Nutzer handelt nicht
 
REGEL
if trust_score < 5:
 → keine echte Bewegung möglich
 → nur Vorbereitung auf Bewegung
10. BLOCKER LOGIK
if trust_confidence < 0.4:
   blocker = TRUST
   intervention = CLARIFY (soft)
 
elif trust_score < 4:
   blocker = TRUST
   intervention = SAFETY
 
elif 4 <= trust_score < 7:
   blocker = TRUST
   intervention = TRUST BUILD
 
elif trust_score >= 7:
   TRUST ist kein Blocker

11. GATE LOGIK (KRITISCH)
Wenn Trust < 5:
→ KEINE Eskalation
→ KEIN Pitch
→ KEINE Aktivierung
→ KEINE Verbindlichkeit
 
Trust blockiert:
→ Monetarisierung
→ Abschluss
→ Tiefe
→ echte Bewegung
 
12. INTERVENTIONSTYPEN (GESCHÄRFT)
SAFETY
Ziel: Sicherheitsgefühl erhöhen
Regeln:
→ keine Bewertung
→ keine Überzeugung
→ keine Argumentation
→ keine Rechtfertigung
 
TRUST BUILD
Ziel: Glaubwürdigkeit aufbauen
Regeln:
→ konkrete Beispiele
→ transparente Aussagen
→ nachvollziehbare Logik
→ keine Übertreibung

CLARIFY
Ziel: Unsicherheit klären
Regeln:
→ offene Frage
→ keine Interpretation
→ keine Richtung vorgeben
 
13. INTERVENTIONSREGEL

Wenn TRUST Blocker ist:
→ keine Lösung
→ kein Produkt
→ kein Pitch
→ kein Druck
 
14. LANGUAGE RULE

Bei niedrigem Trust:
→ keine Claims
→ keine Übertreibung
→ keine Versprechen
→ keine Dominanz
 
Bei hohem Trust:
→ klare, direkte Sprache erlaubt
 
15. EXIT CONDITION (GEHÄRTET)
if trust_score >= 7
AND trust_confidence >= 0.7
AND keine negativen Signale in den letzten 2 Interaktionen:
   TRUST = resolved

16. EDGE CASES
Fake Trust
→ höflich, aber nicht offen
→ confidence reduzieren
 
High State + Low Trust
→ kritischster Zustand
Regel:
→ NICHT erklären
→ NICHT überzeugen
→ nur Trust lösen
 
Widerspruch
→ reduziert confidence
→ verhindert harte Entscheidung
 
17. SYSTEMROLLE
 
Trust ist der primäre Gate-Layer.
Ohne Trust:
→ keine Offenheit
→ keine Verarbeitung
→ keine Entscheidung
→ keine Conversion
 
18. ESSENZ
Trust beantwortet:
Ist Bewegung überhaupt möglich oder muss zuerst Sicherheit entstehen?