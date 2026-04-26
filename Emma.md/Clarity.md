CORE-FRAGE
Versteht die Person konkret, was passiert und was der nächste Schritt für sie bedeutet?
 
2. DEFINITION
CLARITY misst:
wie konkret, greifbar und übersetzbar ein Inhalt für den Nutzer ist
 
NICHT
theoretisches Verständnis
Zustimmung ohne Tiefe
„klingt logisch“

SONDERN
konkrete Vorstellung
Übertragbarkeit in eigene Realität
klares Ergebnisbild
Klarheit über den nächsten Schritt
 
KERNUNTERSCHEIDUNG
State = erkennt das Problem
Clarity = versteht Lösung + Weg
 
CLARITY SPLIT (NEU – KRITISCH)
CLARITY besteht aus zwei Ebenen:
1. Cognitive Clarity
→ versteht das Konzept
→ kann es logisch nachvollziehen
 
 
2. Action Clarity
→ versteht konkret, was zu tun ist
→ kann nächsten Schritt benennen
 
HARTE REGEL
Hohe Cognitive Clarity ohne Action Clarity
→ maximal clarity_score = 6
Ohne Action Clarity keine Bewegung
 
3. SCORE SYSTEM
clarity_score: 0–10
clarity_confidence: 0–1
4. SCORE INTERPRETATION
Score​​​​Zustand​​Bedeutung
0–2​​​​blind​​​versteht nichts
3–4​​​​verwirrt​​diffus, unscharf
5–6​​​​grob​​​versteht Idee
7–8​​​​klar​​​versteht Anwendung
9–10​​​​konkret​​kann es selbst erklären + handeln
 
5. SIGNAL-EINHEIT
 
Ein Signal ist eine Aussage zu:
Verständnis
Verwirrung
Übersetzung
Ergebnisbild
Handlung
 
 
6. SIGNALTYPEN (ULTRA SCHARF)
6.1 CONFUSION SIGNAL (kritisch)
Beispiele:
„Verstehe ich nicht“
„Wie genau meinst du das?“
„Ich sehe das nicht“
 
Wirkung:
→ -2 bis -3
→ clarity_confidence ↓
 
6.2 ABSTRACT SIGNAL
Beispiele:
„Klingt logisch“
„Macht Sinn“
„Verstehe ich“
Wirkung:
→ +0 bis +1
→ kein echtes Movement
 
Fake Clarity Risiko
 
6.3 PARTIAL TRANSLATION SIGNAL
Beispiele:
„Also grob heißt das…“
„Dann würde das wohl bedeuten…“
 
Wirkung:
→ +2
 
6.4 CONCRETE TRANSLATION SIGNAL
 
Beispiele:
„Dann würden die Fragen nicht mehr bei mir landen“
„Dann könnte mein Team das selbst machen“
Wirkung:
→ +3
 
6.5 NEXT-STEP SIGNAL
 
Beispiele:
„Was wäre der erste Schritt?“
„Wie setze ich das konkret um?“
Wirkung:
→ +2 bis +3
 
6.6 MISINTERPRETATION SIGNAL
 
Beispiele:
„Also geht es darum, mehr Content zu machen?“
„Heißt das, ich muss alles neu aufbauen?“
 
Wirkung:
→ -2
→ confidence ↓
7. SIGNALVERARBEITUNG
clarity_score += signal_delta
clarity_confidence += confidence_delta
 
REGELN
abstrakte Zustimmung zählt minimal
konkrete Übersetzung zählt maximal
falsches Verständnis > kein Verständnis (kritischer)
 
8. MICRO-SIGNAL PATTERNS (KRITISCH)
PATTERN 1: FAKE CLARITY
User:
→ „Ja, macht Sinn“
Regel:
kein Score-Anstieg
confidence senken
PATTERN 2: INTELLECTUAL AGREEMENT
 
User versteht logisch, aber nicht praktisch
Regel:
clarity_score max = 6
PATTERN 3: OVERLOAD
 
User:
→ viele Fragen
→ springt Themen
 
Regel:
→ clarity ↓
→ Ease wahrscheinlich ↓
 
PATTERN 4: FALSE SIMPLIFICATION
 
User vereinfacht falsch
Regel:
→ Misinterpretation
→ REFRAME notwendig
 
9. MOVEMENT IMPACT
 
CLARITY blockiert:
1. Entscheidung
→ „Ich verstehe es nicht genug, um ja zu sagen“
 
2. Umsetzung
→ „Ich weiß nicht, wie ich anfangen soll“
 
3. Vertrauen indirekt
→ Unsicherheit erzeugt Skepsis
 
HARTE REGEL
if clarity_score < 5:
→ keine echte Entscheidung möglich
 
10. MOVEMENT MAPPING (NEU – KRITISCH)
clarity_score < 4 → kein Movement möglich
clarity_score 5–6 → Cognitive Movement möglich
clarity_score ≥ 7 → Intent Movement möglich
clarity_score ≥ 8 → Action Movement möglich

verbindet Clarity direkt mit Movement System
 
11. BLOCKER LOGIK
if clarity_confidence < 0.4:
   blocker = CLARITY
   intervention = CLARIFY
 
elif clarity_score < 4:
   blocker = CLARITY
   intervention = REDUCE
 
elif 4 <= clarity_score < 7:
   blocker = CLARITY
   intervention = STRUCTURE
 
elif clarity_score >= 7:
   CLARITY ist kein Blocker
 
12. INTERVENTIONS-MAPPING
Zustand​​​​Intervention
blind​​​​​CLARIFY
verwirrt​​​​REDUCE
grob​​​​​STRUCTURE
klar​​​​​ACTIVATE möglich
 
13. CLARITY vs EASE (NEU – KRITISCH)
CLARITY ≠ HANDHABBARKEIT
REGEL
Wenn:
Clarity hoch
Ease niedrig
Dann:
→ KEIN Clarity Blocker#
→ Ease priorisieren
verhindert falsche Intervention
 
14. LANGUAGE RULE
Niedrige Clarity
einfache Sprache
ein Konzept
konkrete Beispiele
kein Jargon
 
Mittlere Clarity
einfache Struktur
klare Zusammenhänge
 
Hohe Clarity
direkte Sprache
keine Vereinfachung
HARTE REGEL
maximal 1 Konzept pro Antwort bei niedriger Clarity
 
Overload = Clarity Drop
 
15. EXIT CONDITION (GEHÄRTET)
clarity_score ≥ 7
AND clarity_confidence ≥ 0.7
AND Nutzer kann:
→ selbst erklären
→ konkretes Beispiel geben
→ nächsten Schritt benennen
 
 
16. EDGE CASES
Fake Clarity
→ Zustimmung ohne Tiefe
→ confidence ↓
 
High Trust + Low Clarity
→ Conversion Killer
 
Regel:
→ nicht pitchen
→ zuerst Klarheit
 
High State + Low Clarity
→ erkennt Problem, versteht Lösung nicht
Regel:
→ STRUCTURE + Beispiele
 
Misinterpretation
→ sofort REFRAME
 
17. FAILURE MODES
1. OVER-EXPLAINING
→ mehr Infos = weniger Klarheit

2. FEATURE DUMP
→ zerstört Clarity sofort

3. THEORETICAL TALK
→ kein Movement
 
 
4. SKIPPING STEPS
→ zu früh ACTIVATE
 
18. SYSTEMROLLE
 
CLARITY ist:
der Übersetzungs-Layer zwischen Denken und Handeln
 
OHNE CLARITY
kein Verständnis
kein Vertrauen in Handlung
kein Momentum
keine Conversion
 
19. ESSENZ
CLARITY beantwortet:
Kann die Person sich konkret vorstellen, was passiert und was sie jetzt tun würde?