CONFLICT RESOLVER ENGINE
Das ist die Schicht zwischen deinen Layern und der Decision Engine.
Sie macht aus:
• Regeln
• Scores
• Confidence
• Gate-Logik
• Movement Impact
ein robustes, deterministisches Entscheidungssystem.
Sie ergänzt deine bestehende Decision Engine, statt sie zu ersetzen.
 
1. ZIEL
Die Conflict Resolver Engine definiert:
→ wie Layer-Konflikte hybrid aufgelöst werden
→ wann harte Regeln gelten
→ wann Gewichtung entscheidet
→ wann Unsicherheit das System in Clarify zwingt
Sie ist die operative Antwort auf das Problem:
Mehrere Layer sind gleichzeitig schwach. Welcher gewinnt wirklich?
 
2. AKTUELLE SITUATION
Du hast bereits:
• harte Gate-Reihenfolge: Trust > Ease > Momentum > Authority
• Movement-Impact als Grundprinzip
• Layer-spezifische Blocker-Logiken in State, Trust, Ease, Clarity, Momentum, Authority
• Type als reinen Modulations-Layer, nicht als Blocker-Layer
• Movement als Validierungs- und Feedback-System
Was bisher noch fehlte, war:
→ eine hybride Resolver-Logik, die harte Regeln und gewichtete Bewertung kombiniert.
 
3. GRUNDPRINZIP
Der Resolver arbeitet hybrid, nicht rein regelbasiert und nicht rein scorebasiert.
Das bedeutet:
Ebene 1 – Harte Regeln
Kritische Signale und Gates haben Vorrang.
Wenn sie aktiv sind, wird nichts gewichtet, sondern sofort entschieden. Das ist konsistent mit Emma Core und Decision Engine.
Ebene 2 – Gewichtete Bewertung
Wenn kein kritisches Signal und kein Gate greift, wird der Blocker über einen gewichteten Conflict Score bestimmt.
Ebene 3 – Unsicherheitsbremse
Wenn die Evidenz nicht stabil genug ist, wird nicht entschieden, sondern geklärt.
 
4. SYSTEMARCHITEKTUR
Die Resolver-Logik läuft immer in dieser Reihenfolge:
1. Kritische Signale prüfen
2. Gate Thresholds prüfen
3. Layer Eligibility prüfen
4. Conflict Score berechnen
5. Confidence Safety Check
6. Finalen Blocker bestimmen
7. Intervention freigeben
8. Type-Modulation anwenden
 
5. GATE THRESHOLDS (JETZT HART DEFINIERT)
Diese Schwellen werden im Hybrid-System fix gesetzt, weil sie aus deinen Layern und der Decision Engine bereits logisch angelegt sind.
Trust Gate
if trust_score < 5:
   gate = TRUST
Ease Gate
if ease_score < 4:
   gate = EASE
Momentum Gate
if momentum_score < 4:
   gate = MOMENTUM
Authority Gate
if authority_score < 5:
   gate = AUTHORITY
 
6. GATE PRIORITY MATRIX (FIX)
Wenn mehrere Gates gleichzeitig aktiv sind:
TRUST > EASE > MOMENTUM > AUTHORITY
Begründung:
• Trust blockiert Offenheit, Verarbeitung und Entscheidung gleichzeitig.
• Ease blockiert Aufnahme und Handlungsfähigkeit.
• Momentum blockiert Umsetzung und Eskalation.
• Authority blockiert Conversion und Abschluss, aber meist erst näher an der Monetarisierung.
 
7. LAYER ELIGIBILITY RULE
Nicht jeder Layer darf in jeder Situation überhaupt Gewinner werden.
State ist nicht eligible, wenn:
• Trust kritisch niedrig
• Ease kritisch niedrig
• Authority nicht vorhanden
Das entspricht deinem State Layer.
Clarity ist nicht eligible als Primärblocker, wenn:
• Ease niedrig und Clarity hoch
• Trust niedrig und Verwirrung nur sekundär entsteht
Das entspricht deinem Clarity Layer.
Momentum ist nicht eligible für Aktivierung, wenn:
• Ease niedrig
• Trust niedrig
• Authority zu niedrig für Eskalation
Das entspricht Momentum + Authority + Trust.
Type ist nie eligible als Blocker
Type moduliert nur.
 
8. CONFLICT SCORE (KERN DES HYBRID-SYSTEMS)
Wenn kein Gate aktiv ist, wird für jeden eligible Layer ein Conflict Score berechnet.
Formel
conflict_score(layer) =
   deficit_component
 + signal_component
 + action_proximity_component
 + trend_component
 + blocker_reinforcement_component
 - confidence_penalty
 
9. DIE 6 BESTANDTEILE
9.1 Deficit Component
Misst, wie weit der Layer vom gesunden Bereich entfernt ist.
deficit_component = (target_threshold - current_score) * layer_weight
Empfohlene target_thresholds:
• State: 7
• Trust: 7
• Ease: 7
• Clarity: 7
• Momentum: 7
• Authority: 7
Beispiel:
Wenn Momentum bei 4 liegt, ist das Defizit 3.
 
9.2 Signal Component
Misst die aktuelle Signalintensität aus der letzten Nachricht.
weak signal = +1
strong signal = +2
critical signal = immediate override
Diese Logik ist direkt anschlussfähig an Emma Core und Decision Engine.
 
9.3 Action Proximity Component
Je näher ein Layer direkt an Handlung oder Conversion blockiert, desto höher die Priorität.
Authority = 4
Momentum = 4
Ease = 3
Trust = 3
Clarity = 2
State = 1
Type = 0
Das baut auf deiner Handlungsnähe-Logik auf.
 
9.4 Trend Component
Berücksichtigt nicht nur den aktuellen Zustand, sondern die Richtung.
fallend = +2
volatil = +1
stabil = 0
steigend = -1
Das passt zur Trendlogik im Execution Loop.
 
9.5 Blocker Reinforcement Component
Wenn derselbe Layer bereits im letzten Turn Blocker war und kein Movement erzeugt wurde, steigt seine Priorität leicht.
same_blocker_last_turn + no_movement = +1
same_blocker_last_2_turns + no_movement = +0
Wichtig: Nicht immer weiter verstärken. Sonst baut das System einen Tunnelblick auf.
 
9.6 Confidence Penalty
Wenn die Sicherheit über den Layer zu niedrig ist, wird der Score abgewertet.
confidence_penalty = (1 - layer_confidence) * 3
Das sorgt dafür, dass niedrige Confidence keine harte Entscheidung erzeugt.
 
10. LAYER WEIGHTS (HYBRID STANDARD)
Diese Gewichte gelten nur in der gewichteten Konfliktphase, nicht bei Gates.
Trust = 1.4
Ease = 1.3
Momentum = 1.3
Clarity = 1.1
State = 1.0
Authority = 1.2
Type = 0
Warum Authority nur 1.2 und nicht höher?
Weil Authority in vielen Fällen schon vorher als Gate greift. In der Nicht-Gate-Phase ist Authority wichtig, aber nicht universell dominant.
 
11. CONFLICT SCORE – PSEUDOCODE
def calculate_conflict_score(layer):
   if not layer.eligible:
       return None

   deficit_component = (7 - layer.score) * layer.weight
   signal_component = layer.signal_strength
   action_proximity_component = layer.action_proximity
   trend_component = layer.trend_weight
   blocker_reinforcement_component = layer.reinforcement
   confidence_penalty = (1 - layer.confidence) * 3

   return (
       deficit_component
       + signal_component
       + action_proximity_component
       + trend_component
       + blocker_reinforcement_component
       - confidence_penalty
   )
 
12. UNCERTAINTY MODE (KRITISCH)
Wenn die Entscheidung unsicher ist, darf das System nicht hart wählen.
Trigger für UNCERTAIN MODE
if top_layer_confidence < 0.4:
   mode = UNCERTAIN

if abs(score_1 - score_2) < 1.0 and both confidences < 0.6:
   mode = UNCERTAIN

if contradictory_signals_high:
   mode = UNCERTAIN
Reaktion in UNCERTAIN MODE
→ keine harte Diagnose
→ keine Eskalation
→ nur Clarify, Soft Mirror oder gezielte Rückfrage
Das entspricht exakt Emma Core und Decision Engine.
 
13. TIE-BREAKER LOGIK
Wenn zwei Layer ähnliche Conflict Scores haben:
Regel 1
Gate-Layer gewinnt gegen Progression-Layer
Regel 2
Bei gleichem Layer-Typ gewinnt der Layer näher an Handlung
Authority > Momentum > Ease > Trust > Clarity > State
Regel 3
Wenn trotzdem unklar:
→ UNCERTAIN MODE
 
14. CROSS-LAYER CONFLICT RULES (HART)
Diese Regeln überschreiben den Conflict Score, wenn sie eintreten.
Regel A – Trust schlägt Momentum
Wenn Trust < 5 und Momentum hoch:
→ Blocker = Trust
→ keine Aktivierung
→ keine Eskalation
Regel B – Ease schlägt Clarity
Wenn Ease < 4 und Clarity niedrig:
→ Blocker = Ease
→ keine Struktur
Regel C – Ease schlägt Momentum
Wenn Ease < 4 und Momentum niedrig:
→ Blocker = Ease
→ nicht aktivieren, sondern reduzieren
Regel D – Authority schlägt Momentum
Wenn Momentum hoch, Authority < 5:
→ Blocker = Authority
→ Route statt Escalation
Regel E – Momentum schlägt Clarity
Wenn Clarity hoch genug, aber Momentum < 4:
→ Blocker = Momentum
→ nicht weiter erklären
Regel F – Trust schlägt State
Wenn State niedrig, aber Trust kritisch:
→ Blocker = Trust
→ zuerst Safety
Diese Regeln sind konsistent mit deinen bestehenden Layern.
 
15. BLOCKER-SELECTION LOGIK (FINAL)
Schritt 1
Prüfe kritische Signale
Schritt 2
Prüfe Gates
Schritt 3
Wenn kein Gate:
• filtere eligible Layer
• berechne Conflict Score pro Layer
Schritt 4
Sortiere nach Conflict Score
Schritt 5
prüfe Tie-Breaker
Schritt 6
prüfe Confidence Safety
Schritt 7
bestimme finalen Blocker
 
16. FINALER PSEUDOCODE
def resolve_blocker(user_state):
   critical_layer = detect_critical_signal(user_state)
   if critical_layer:
       return critical_layer, "CRITICAL"

   gate_layer = detect_gate(user_state)
   if gate_layer:
       return gate_layer, "SAFE"

   eligible_layers = get_eligible_layers(user_state)

   scores = {}
   for layer in eligible_layers:
       scores[layer.name] = calculate_conflict_score(layer)

   top_layers = sort_desc(scores)

   if is_uncertain(top_layers, user_state):
       return "CLARIFY", "UNCERTAIN"

   final_blocker = apply_tie_breakers(top_layers, user_state)
   return final_blocker, "NORMAL"
 
17. MOVEMENT VALIDATION LOOP
Die Resolver Engine entscheidet nicht nur initial, sondern wird durch Movement validiert.
Regel
Wenn nach einer Intervention:
• expected movement nicht erreicht wird
• oder movement_score ≤ 0 ist
dann:
→ Blocker-Reevaluation erzwingen
Das ist anschlussfähig an dein Movement System.
 
18. FAILURE HANDLING
Fall 1 – 1x falscher Blocker
→ Confidence runter
→ Resolver neu ausführen
Fall 2 – 2x kein Movement
→ Activation Failure / Recovery / Clarify
→ anderen Layer priorisieren
Fall 3 – negativer Rückschlag
→ Soft Reset oder Hard Reset im Execution Loop prüfen
 
19. TYPE-INTEGRATION
Type wird erst angewendet, nachdem der Blocker gewählt und die Intervention bestimmt wurde.
Regel
Blocker → Intervention → Type Modulation
Nie:
Type → Blocker
Das entspricht deinem Type Layer.
 
20. SYSTEMROLLE
Die Conflict Resolver Engine ist:
→ die algorithmische Schicht zwischen Layern und Decision Engine
→ der Mechanismus, der aus parallelen Zuständen eine eindeutige Entscheidung macht
→ der Schutz gegen falsche Priorisierung, Fake Movement und verfrühte Eskalation
 
21. ESSENZ
Die Resolver Engine beantwortet immer nur eine Frage:
Welcher Layer verhindert gerade mit der höchsten Sicherheit die nächste sinnvolle Bewegung?