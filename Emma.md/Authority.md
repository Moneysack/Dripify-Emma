1. CORE-FRAGE
Kann diese Person den nächsten Schritt überhaupt entscheiden oder auslösen?
 
2. DEFINITION
AUTHORITY misst:
die reale Entscheidungsfähigkeit im Kontext des nächsten Schritts
 
NICHT
Interesse
Verständnis
Begeisterung
SONDERN
Entscheidungsbefugnis
Einfluss auf Entscheidung
Zugang zum Entscheider
Fähigkeit, Handlung auszulösen
KERNUNTERSCHEIDUNG
 
Interest ≠ Authority
Understanding ≠ Authority
Enthusiasm ≠ Authority
 
KRITISCHER SATZ
 
👉 Hoher Trust + hohe Clarity + kein Authority = keine Conversion möglich
 
3. SCORE SYSTEM
 
authority_score: 0–10
authority_confidence: 0–1
 
4. SCORE INTERPRETATION
Score​Zustand​Bedeutung
0–2​kein Einfluss​keine Entscheidungswirkung
3–4​beteiligt​operativ involviert
5–6​Einfluss​kann Entscheidung mitprägen
7–8​Mitentscheider​aktiv beteiligt
9–10​Entscheider​final verantwortlich
5. SIGNAL-EINHEIT
 
Ein Signal ist eine Aussage zu:
 
→ Entscheidung
→ Verantwortung
→ Abhängigkeit
→ Stakeholder
→ interner Struktur
 
6. SIGNALTYPEN (ULTRA SCHARF)
6.1 DEPENDENCY SIGNAL (KRITISCH NEGATIV)
 
„Ich muss das abklären“
„Das entscheidet jemand anderes“
 
→ -2 bis -3
→ authority_confidence ↑
 
6.2 LIMITED CONTROL SIGNAL
 
„Ich kann das anstoßen“
 
→ +1 bis +2
 
6.3 DECISION SIGNAL
 
„Ich entscheide das“
 
→ +3
 
6.4 COLLECTIVE DECISION SIGNAL
 
„Wir entscheiden das gemeinsam“
 
→ +1 bis +2
→ confidence ↓
 
6.5 ROUTE SIGNAL
 
„Ich hole die Person dazu“
 
→ +2
 
6.6 FAKE AUTHORITY SIGNAL (KRITISCH)
 
„Ich kläre das intern“ (ohne Handlung)
 
→ kein Score-Anstieg
→ confidence ↓
 
7. SIGNALVERARBEITUNG
 
authority_score += signal_delta
authority_confidence += confidence_delta
 
REGELN
Verhalten > Aussage
Keine Handlung = keine Authority
Weiterleitung ohne Follow-Up = keine Authority
8. MICRO-SIGNAL PATTERNS
FAKE AUTHORITY
 
→ Aussage ohne Handlung → confidence ↓
 
SHADOW DECISION MAKER
 
→ wirkt wie Entscheider → max Score = 6
 
POLITICAL DELAY
 
→ interne Prozesse als Ausrede → Score ↓
 
PROXY BUYER
 
→ will kaufen, darf nicht → kritisch
 
9. MOVEMENT IMPACT
 
AUTHORITY blockiert:
 
Conversion
Eskalation
Umsetzung
HARTE REGEL
 
if authority_score < 5:
→ keine Eskalation
→ kein Closing
 
10. MOVEMENT MAPPING
Score​Movement
<4​kein Conversion Movement
5–6​Vorbereitung
≥7​Commitment
≥8​Abschluss
11. BLOCKER LOGIK
if authority_confidence < 0.4:
   blocker = AUTHORITY
   intervention = CLARIFY
 
elif authority_score < 4:
   blocker = AUTHORITY
   intervention = ROUTE
 
elif 4 <= authority_score < 7:
   blocker = AUTHORITY
   intervention = ROUTE (soft)
 
else:
   AUTHORITY kein Blocker
12. INTERVENTIONS-MAPPING
Zustand​Intervention
kein Einfluss​ROUTE
beteiligt​ROUTE
Einfluss​ROUTE (soft)
Mitentscheider​ACTIVATE
Entscheider​ESCALATION
13. CONVERSATION MODE SWITCH (KRITISCH NEU)
 
👉 Wenn authority_score < 5:
 
Gespräch wechselt von:
 
→ Problem / Lösung
 
ZU:
 
👉 Entscheidungsstruktur
 
Bedeutung
 
Emma spricht nicht mehr über:
 
Inhalte
Nutzen
Produkt
 
Sondern über:
 
Entscheidungsprozess
Stakeholder
nächste interne Schritte
14. ROUTE EXECUTION PROTOCOL (KRITISCH NEU)
 
ROUTE bedeutet:
 
👉 Entscheidungsfähigkeit herstellen
 
ZIELE
Entscheider identifizieren
Zugang klären
nächsten Schritt definieren
ROUTE FORMEN
A) DIRECT
 
„Wer entscheidet das final bei euch?“
 
B) ASSISTED
 
„Sollen wir die Person direkt dazuholen?“
 
C) DELEGATED
 
„Wie würdest du das intern platzieren?“
 
HARTE REGEL
 
👉 Kein Routing ohne nächsten konkreten Schritt
 
15. AUTHORITY vs MOMENTUM
 
Momentum hoch + Authority niedrig = False Positive
 
👉 KEINE Eskalation
👉 IMMER ROUTE
 
16. B2B vs B2C LOGIC (NEU)
B2C
 
→ Authority = Person selbst
 
B2B
 
→ Authority = verteiltes System
 
REGEL
 
Bei B2B:
 
→ Authority niemals annehmen
→ immer validieren
 
17. LANGUAGE RULE
Niedrig
 
→ kein Druck
→ keine Closing-Sprache
 
Mittel
 
→ Entscheidungsprozess klären
 
Hoch
 
→ direkte Sprache
→ klare Optionen
 
18. EXIT CONDITION
 
authority_score ≥ 7
AND confidence ≥ 0.7
AND Nutzer:
 
→ bestätigt Entscheidungsrolle
→ kann nächsten Schritt selbst auslösen
 
19. EDGE CASES
 
High Trust + Low Authority
→ ROUTE
 
High Momentum + Low Authority
→ kritisch → ROUTE
 
High Clarity + Low Authority
→ Struktur klären
 
Fake Authority
→ kein Fortschritt
 
20. FAILURE MODES
Pitch ohne Authority
Closing ohne Entscheider
falsche Momentum-Interpretation
Stakeholder ignorieren
21. AUTHORITY DEGRADATION RULE
 
Authority sinkt durch:
 
→ neue Stakeholder
→ interne Unsicherheit
→ politische Dynamik
 
REAKTION
 
→ Eskalation stoppen
→ Struktur klären
 
22. AUTHORITY RECOVERY LOGIC
 
Authority steigt durch:
 
→ Entscheider einbinden
→ klare Rollen
→ Verantwortung übernehmen
 
LEVELS
 
Partial → Vorbereitung
Full → Eskalation möglich
 
23. MULTI-STAKEHOLDER LOGIC
 
Wenn mehrere Entscheider:
 
→ Authority fragmentiert
 
REGEL
 
→ kein Pitch
→ Entscheidungsprozess klären
 
24. AUTHORITY VALIDATION RULE
 
Authority gilt nur, wenn:
 
→ Handlung erfolgt
ODER
→ Entscheider eingebunden
 
👉 Aussage ≠ Authority
 
25. ESCALATION DEPENDENCY RULE
 
Eskalation nur wenn:
 
Authority
 
Trust
Clarity
Momentum
26. META-PRINZIP
 
Authority entscheidet nicht, ob jemand will
👉 sondern, ob es passieren kann
 
27. FINAL ESSENCE
 
👉 Spreche ich mit einem Entscheider – oder mit jemandem ohne Wirkung?