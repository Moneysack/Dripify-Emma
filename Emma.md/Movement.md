MOVEMENT SYSTEM
 
1. ZWECK
Das Movement System definiert:
→ ob eine Intervention Wirkung erzeugt hat
→ wie stark diese Wirkung ist
→ ob Fortschritt im System stattfindet
→ wie die nächste Entscheidung beeinflusst wird
→ wie sich der Zustand des Nutzers dynamisch weiterentwickelt
 
Die Decision Engine entscheidet:
→ WAS getan wird
Das Intervention System bestimmt:
→ WIE reagiert wird
Das Movement System bestimmt:
→ OB es funktioniert hat
 
2. GRUNDPRINZIP
Movement ist die primäre Erfolgsmetrik im System.
Movement = Zustandsveränderung + Verhaltensveränderung  
 
Movement ist nicht:
→ Klick
→ Kauf
→ Antwortlänge
Sondern:
→ messbare Veränderung im Zustand UND Verhalten
 
 
3. MOVEMENT DIMENSIONEN
3.1 STATE MOVEMENT (intern)
Veränderung in den Layern:
→ State
→ Trust
→ Ease
→ Clarity
→ Momentum
→ Authority
 
3.2 BEHAVIOR MOVEMENT (extern)
Veränderung im Verhalten:
→ Tiefe der Aussage
→ Klarheit der Sprache
→ Offenheit
→ Reaktion auf Intervention
→ konkrete Handlung
 
4. MOVEMENT LEVEL SYSTEM
 
LEVEL 0 – NO MOVEMENT
→ keine Veränderung
→ Wiederholung / Ausweichen / Ignorieren
 
LEVEL 1 – MICRO MOVEMENT
→ minimale Öffnung
→ leichte Zustimmung
 
LEVEL 2 – COGNITIVE MOVEMENT
→ Denkweise verändert sich
→ Problem wird klarer erkannt
 
LEVEL 3 – EMOTIONAL MOVEMENT
→ Schutz sinkt
→ Vertrauen steigt
→ Offenheit nimmt zu
 
LEVEL 4 – INTENT MOVEMENT
→ Bereitschaft zur Handlung
→ echtes Interesse
 
LEVEL 5 – ACTION MOVEMENT
→ reale, relevante Handlung im System
 
5. ACTION DEFINITION (GESCHÄRFT)
Action Movement ist nur erfüllt, wenn:
→ Handlung ist relevant für den Fortschritt im System
 
KEIN ACTION MOVEMENT
→ Klick ohne Kontext
→ kurze Zustimmung
→ oberflächliche Antwort
 
ECHTES ACTION MOVEMENT
→ klare Entscheidung
→ konkrete Umsetzung
→ aktiver nächster Schritt
 
6. MOVEMENT SCORE
movement_score: -2 bis +5  
 
NEGATIVES MOVEMENT
Rückzug → -2
Skepsis steigt → -1
Verwirrung → -1
Themenwechsel → -1
 
POSITIVES MOVEMENT
Micro → +1
Cognitive → +2
Emotional → +3
Intent → +4
Action → +5
 
7. MOVEMENT DETECTION
Movement wird erkannt durch:
 
7.1 LAYER SHIFT
delta_layer_score > 1
 
7.2 SIGNAL SHIFT
→ Symptom → Muster
→ Skepsis → Offenheit
→ defensiv → ehrlich
 
7.3 BEHAVIOR SHIFT
→ konkretere Aussagen
→ neue Fragen
→ mehr Tiefe
→ Handlung
 
8. FAKE MOVEMENT DETECTION (NEU)
Nicht jede positive Reaktion ist echtes Movement.
FAKE MOVEMENT SIGNATURE
→ kurze Zustimmung ohne Tiefe
→ kein Follow-up
→ keine Veränderung im Layer
→ keine Anschlusshandlung
 
REGEL
Wenn:
→ Verhalten positiv wirkt
ABER
→ keine Layer-Veränderung
Dann:
movement_score = max +1
confidence reduzieren
 
9. INTERVENTION → EXPECTED MOVEMENT (NEU)
Jede Intervention hat ein erwartetes Minimum:
Intervention
Expected Movement
MIRROR
Level 1–2
REFRAME
Level 2–3
SAFETY
Level 2–3
TRUST BUILD
Level 3–4
CLARIFY
Level 1–2
REDUCE
Level 1–2
STRUCTURE
Level 2–4
ACTIVATE
Level 4–5
ROUTE
Level 3–5
NAME
Level 3–4
 
VALIDIERUNGSREGEL
Wenn:
→ tatsächliches Movement < erwartetes Movement
Dann:
→ Intervention nicht erfolgreich
 
10. MOVEMENT → LAYER FEEDBACK LOOP (NEU)
Movement beeinflusst aktiv die Layer.
 
REGEL
Wenn Movement erkannt wird:
→ entsprechende Layer werden angepasst
 
BEISPIELE
Cognitive Movement → State + Clarity ↑
Emotional Movement → Trust + Ease ↑
Intent Movement → Momentum ↑
Action Movement → Momentum + Authority ↑
 
NEGATIVES MOVEMENT
→ Trust ↓
→ Momentum ↓
→ Ease ↓
 
11. MOVEMENT INTERPRETATION
 
REGEL 1
Kein Movement → Intervention oder Blocker falsch
 
REGEL 2
Movement bestimmt nächsten Schritt
 
REGEL 3
Movement validiert Systementscheidung
 
12. MOVEMENT → DECISION ENGINE
 
INTERVENTION VALIDIERUNG
movement_score ≥ 2 → korrekt
movement_score ≤ 0 → falsch
 
BLOCKER VALIDIERUNG
kein Movement → Blocker prüfen
 
ESKALATIONSFREIGABE
movement_score ≥ 4 + Layer ok → Eskalation erlaubt
 
13. FAILURE LOGIK
Wenn:
→ 2x kein Movement
Dann:
→ Intervention wechseln
→ Blocker neu bewerten
→ CLARIFY aktivieren
 
14. MOVEMENT MEMORY
 
REGELN
→ Trend wichtiger als Einzelwert
→ 3 kleine Movements = 1 großes
→ negativer Trend hat Vorrang
 
15. MOVEMENT PATTERN
 
POSITIV
→ steigende Klarheit
→ steigendes Vertrauen
→ steigendes Momentum
 
NEGATIV
→ wiederkehrende Skepsis
→ Rückzug
→ sinkende Tiefe
 
16. SYSTEMROLLE
Movement System ist:
→ Feedback-System
→ Validierungssystem
→ Steuerlogik
 
17. INTEGRATION
Movement beeinflusst:
→ Decision Engine
→ Intervention System
→ Layer System
→ Execution Loop
 
18. ESSENZ
Intervention → Movement → Layer Update → neue Entscheidung
 
 
Zentrale Frage:
Hat sich der Zustand UND das Verhalten verändert?
 
19. KERNREGELN
1. Movement ist die primäre KPI
2. Kein Movement = falsche Intervention oder falscher Blocker
3. Expected Movement definiert Erfolg
4. Fake Movement muss erkannt werden
5. Movement beeinflusst Layer aktiv
6. Eskalation nur bei echtem Movement