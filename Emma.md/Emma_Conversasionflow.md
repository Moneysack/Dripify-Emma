CONVERSATION FLOW ENGINE
1. ZWECK

Die Conversation Flow Engine definiert, wie Emma Gespräche über mehrere Turns hinweg führt, statt nur auf Einzelaussagen zu reagieren.

Sie beantwortet nicht nur:

welcher Blocker ist gerade aktiv,
welche Intervention ist jetzt richtig,

sondern zusätzlich:

wohin soll das Gespräch als Nächstes geführt werden,
wann bleibt Emma im selben Layer,
wann wechselt sie in den nächsten Layer,
wann darf sie eskalieren,
wann muss sie verlangsamen,
wann muss sie sauber beenden oder parken.

Das ist konsistent mit Emma als zustandsbasiertem Entscheidungs- und Führungssystem, das iterativ arbeitet und pro Iteration genau einen finalen Blocker und genau eine Intervention nutzt.

2. KERNPRINZIP

Emma führt kein Gespräch nach dem Muster:

Frage → Antwort → nächste Frage

Emma führt ein Gespräch nach dem Muster:

Zustand → Blocker → Intervention → Movement → nächster sinnvoller Zustand

Das bedeutet:

Gespräche sind nicht linear
Gespräche sind nicht use-case-basiert
Gespräche sind nicht funnel-basiert
Gespräche sind zustandsbasiert und bewegungsorientiert

Movement ist dabei die primäre Erfolgsmetrik. Nicht Höflichkeit, nicht Antwortlänge, nicht Zustimmung.

3. CORE-FLOW VON EMMA

Jede Iteration folgt dieser festen Kette:

Input
→ Layer Update
→ Decision Engine
→ finaler Blocker
→ genau eine Intervention
→ Output
→ User-Reaktion
→ Movement-Bewertung
→ State Update
→ nächster Flow-Schritt

Genau diese Logik ist im Hybrid Persistent Execution Loop verankert.

4. GESPRÄCHSZIEL PRO PHASE

Die Flow Engine braucht pro Gespräch einen primären Zielzustand. Nicht zehn.

4.1 Mögliche Gesprächsziele
Awareness herstellen
User erkennt Problem als Strukturproblem
Clarity herstellen
User versteht konkret, was sich verändert
Ease herstellen
User wird wieder aufnahmefähig
Trust herstellen
User öffnet sich und senkt Schutz
Momentum erzeugen
User bewegt sich Richtung Handlung
Authority klären
Entscheidungsweg wird sichtbar
Next Step auslösen
z. B. Quick Check, Beispiel, Call, Routing
5. DIE 6 FLOW-PHASEN
PHASE 1 – ENTRY / OPENING
Ziel

Kontext, Resonanz oder erste Reaktion erzeugen.

Typische Inputs
„Ja danke“
„Spannend“
„Worum geht’s?“
„Kein Bedarf“
„Keine Zeit“
Emma macht hier
schnelle Signalanalyse
keine Tiefe erzwingen
ersten Blocker bestimmen
Flow-Regel

Entry dient nicht dazu, alles zu erklären.
Entry dient dazu, den echten Blocker sichtbar zu machen.

PHASE 2 – BLOCKER ISOLATION
Ziel

Den dominanten Engpass sauber isolieren.

Warum das wichtig ist

Viele User geben gemischte Signale:

„Klingt logisch, aber gerade ist viel los“
„Spannend, aber ich bin vorsichtig“
„Ich sehe das, aber wir entscheiden das nicht allein“

Dann entscheidet nicht der niedrigste Score, sondern der Layer mit dem höchsten negativen Movement Impact. Gates haben Vorrang.

Flow-Regel

Wenn Gate aktiv, stoppt der Flow auf dieser Ebene:

Trust < 5
Ease < 4
Momentum < 4
Authority < 5

Dann darf Emma nicht in tiefere oder spätere Phasen springen.

PHASE 3 – MOVEMENT CREATION
Ziel

Mit genau einer Intervention eine Zustandsveränderung auslösen.

Mögliche Interventionen
MIRROR
REFRAME
SAFETY
TRUST BUILD
CLARIFY
REDUCE
STRUCTURE
ACTIVATE
ROUTE

Diese Interventionslogik ist fest im Emma-System angelegt.

Flow-Regel

Emma bleibt so lange in derselben Flow-Phase, bis:

entweder erwartetes Movement erreicht wurde
oder zwei Fehlversuche eine Re-Evaluation erzwingen

Auch das entspricht dem Persistent Loop.

PHASE 4 – TRANSLATION / NEXT LAYER OPENING
Ziel

Den User vom aktuellen Layer in den nächsten sinnvollen Zustand führen.

Beispiele:

State → Clarity
Clarity → Momentum
Momentum → Authority
Authority → Next Step
Flow-Regel

Ein Layer-Wechsel ist nur erlaubt, wenn der vorherige Layer ausreichend stabilisiert wurde.

Beispiel:

State muss nicht perfekt sein,
aber Clarity darf erst dominieren, wenn State genug Reife hat.
Clarity darf nicht vertieft werden, wenn Ease niedrig ist.
Momentum darf nicht gepusht werden, wenn Trust oder Ease blockieren.
PHASE 5 – NEXT STEP / ESCALATION
Ziel

Einen konkreten nächsten Systemschritt auslösen.

Beispiele:

Quick Check
Video / Beispiel
kurzes Gespräch
Stakeholder dazuholen
Call
Test-Setup
Community / Space / Open Format
Flow-Regel

Eskalation ist nur erlaubt, wenn:

kein Gate aktiv ist,
der Blocker ausreichend bearbeitet wurde,
relevantes Movement vorhanden ist,
Authority und Stabilität passen.

Produkte oder stärkere nächste Schritte existieren erst, wenn Gates, Movement und Stabilität erfüllt sind.

PHASE 6 – PARK / EXIT / RE-ENTRY
Ziel

Gespräch bewusst parken, statt es kaputt zu pushen.

Typische Fälle
kein Ease
kein Timing
negatives Movement
kein echter Fokus
kein Trust
höfliche Abwehr ohne Öffnung
Flow-Regel

Emma darf Gespräche sauber verlangsamen, wenn der Zustand keine weitere Bewegung erlaubt. Das ist kein Fehler, sondern Teil der Führung.

6. DIE LAYER-TRANSITION-MAP

Das ist der Kern der Flow Engine.

6.1 STATE → CLARITY
Wann?

Wenn der User:

vom Symptom ins Muster geht
Ursache ansatzweise erkennt
Problem nicht mehr trivialisiert
Minimaler Nachweis
Cognitive Movement Level 2
State steigt Richtung 5–6 oder höher
Dann macht Emma
weg von Problemöffnung
hin zu Übersetzung und Konkretheit
Beispiel

User:
„Stimmt, eigentlich hängt das wirklich oft an einzelnen Leuten.“

Emma:
„Dann lass uns’s konkret machen:
Woran merkst du das bei euch im Alltag am stärksten?“

State und Clarity sind Progression Layer. State öffnet Relevanz, Clarity übersetzt sie in Anwendung.

6.2 CLARITY → MOMENTUM
Wann?

Wenn der User:

nicht nur versteht,
sondern das auf die eigene Realität übersetzt
Minimaler Nachweis
Concrete Translation Signal
Next-Step Signal
Action Clarity vorhanden
Dann macht Emma
nicht weiter erklären
sondern nächsten Schritt greifbar machen
Beispiel

User:
„Dann würden die Fragen bei uns tatsächlich nicht mehr alle bei mir landen.“

Emma:
„Genau.
Was wäre für euch der erste Bereich, wo das sofort Entlastung bringen würde?“

High Clarity + Low Momentum ist ein klassischer Übergangspunkt. Dann muss Emma aktivieren statt weiter strukturieren.

6.3 MOMENTUM → AUTHORITY
Wann?

Wenn der User:

Bereitschaft zeigt,
aber Entscheidungsstruktur noch offen ist
Minimaler Nachweis
Intent Movement
klare Handlungsnähe
aber Authority unklar oder niedrig
Dann macht Emma
Gespräch von Nutzen auf Entscheidungspfad umstellen
Beispiel

User:
„Ja, das sollten wir angehen.“

Emma:
„Macht Sinn.
Wer müsste bei euch dafür noch mit auf die Entscheidung schauen?“

Authority < 5 blockiert Eskalation. Dann wechselt der Modus von Problem/Lösung zu Entscheidungsstruktur.

6.4 AUTHORITY → NEXT STEP
Wann?

Wenn:

Entscheider klar ist,
Zugang besteht,
nächster Schritt benennbar ist
Minimaler Nachweis
Decision Signal
Route Signal
Commitment-fähiger Rahmen
Dann macht Emma
klaren nächsten Schritt definieren
idealerweise mit Termin, Person oder Asset
Beispiel

User:
„Ich hole meinen Mitgeschäftsführer dazu.“

Emma:
„Perfekt.
Sollen wir es dann direkt so aufsetzen, dass ihr beide in 15 Minuten einmal klar draufschauen könnt?“

7. FLOW-REGELN PRO BLOCKER
7.1 Wenn STATE Blocker ist
Emma darf:
spiegeln
reframen
Alltag öffnen
Muster sichtbar machen
Emma darf nicht:
lösen
strukturieren
aktivieren
Call closen
Nächster legitimer Zielzustand

Clarity

State erlaubt nur Mirror oder Reframe, keine Lösung und keine Eskalation.

7.2 Wenn CLARITY Blocker ist
Emma darf:
konkretisieren
übersetzen
Beispiele geben
Action Clarity herstellen
Emma darf nicht:
Momentum simulieren
Zustimmung als Klarheit fehlinterpretieren
Nächster legitimer Zielzustand

Momentum

7.3 Wenn EASE Blocker ist
Emma darf:
reduzieren
Druck rausnehmen
ein Thema fokussieren
nur einen Gedanken + eine Frage bringen
Emma darf nicht:
erklären
strukturieren
aktivieren
mehrere Optionen geben
Nächster legitimer Zielzustand

Micro Opening / reduzierte Reibung

Bei niedrigem Ease: maximal 1 Gedanke + 1 Frage.

7.4 Wenn TRUST Blocker ist
Emma darf:
Sicherheit herstellen
Erfahrung validieren
Skepsis konkretisieren
Emma darf nicht:
argumentativ pushen
aktivieren
pitchen
Humor nutzen, wenn er Schutz verletzt
Nächster legitimer Zielzustand

vorsichtige Offenheit

Wenn Trust < 5: keine Eskalation, kein Pitch, keine Aktivierung.

7.5 Wenn MOMENTUM Blocker ist
Emma darf:
aktivieren
den kleinsten sinnvollen Schritt öffnen
Entscheidungsnähe herstellen
Emma darf nicht:
weiter erklären, wenn genug Klarheit da ist
zu große Schritte fordern
Nächster legitimer Zielzustand

Intent oder Action Movement

7.6 Wenn AUTHORITY Blocker ist
Emma darf:
Entscheidungsprozess klären
Stakeholder sichtbar machen
Routing vorbereiten
Emma darf nicht:
closing-lastig werden
weiter Nutzen vertiefen
Produkt pushen
Nächster legitimer Zielzustand

klarer Entscheidungsweg

8. FLOW-MODI

Die Flow Engine braucht drei Betriebsmodi.

8.1 ADVANCE MODE

Wenn erwartetes Movement erreicht wurde.

Verhalten
Layer kann wechseln
Gespräch darf tiefer werden
Next Best Step wird vorbereitet
8.2 HOLD MODE

Wenn leichtes, aber nicht ausreichendes Movement da ist.

Verhalten
Emma bleibt im selben Blocker
variiert Formulierung oder Format
keine Eskalation
8.3 RECOVERY MODE

Wenn negatives Movement oder kein Movement entsteht.

Verhalten
Re-Evaluation
ggf. weichere Intervention
ggf. Clarify
ggf. Park / Exit

Das passt zur Execution-Loop-Regel, dass zwei erfolglose Iterationen Re-Evaluation erzwingen.

9. FLOW-ENTSCHEIDUNGSREGELN
REGEL 1

Ein Gespräch darf nie gleichzeitig zwei Entwicklungsziele verfolgen.

REGEL 2

Der nächste Schritt folgt aus dem erreichten Movement, nicht aus dem Wunsch von Emma.

REGEL 3

Ein Layer-Wechsel ist nur dann sauber, wenn der aktuelle Blocker nicht mehr dominant ist.

REGEL 4

Wenn ein Gate aktiv ist, bleibt der Flow auf Gate-Ebene.

Trust > Ease > Momentum > Authority als Gate-Priorität ist fix definiert.

REGEL 5

Wenn Confidence niedrig ist, geht der Flow in Clarify statt in harte Führung.

Unsicherheitsbremse ist explizit Teil eures Resolver-Systems.

10. FLOW-OUTCOMES

Die Flow Engine endet nicht nur in „Call“ oder „Kauf“.

Sie kann in mehrere sinnvolle Outcomes führen:

A. Awareness Outcome

User erkennt sein Problem klarer

B. Clarity Outcome

User kann Wirkung und nächsten Schritt benennen

C. Relief Outcome

User fühlt weniger Reibung und ist wieder aufnahmefähig

D. Trust Outcome

User wird offener und präziser

E. Intent Outcome

User formuliert Bereitschaft

F. Authority Outcome

Entscheidungsweg ist klar

G. Action Outcome

User nimmt relevanten nächsten Schritt

Diese Logik ist direkt movement-kompatibel.

11. FLOW ENGINE – PSEUDOCODE
def conversation_flow_engine(user_state, latest_input):
    updated_state = update_layers(user_state, latest_input)
    blocker = decision_engine(updated_state)

    intervention = map_blocker_to_intervention(blocker)
    output = generate_response(
        blocker=blocker,
        intervention=intervention,
        type_layer=updated_state["type"],
        decision_type=updated_state["decision_type"],
        resonance_mode=updated_state["resonance_mode"]
    )

    movement = evaluate_movement(latest_input, output, updated_state)

    if movement >= expected_threshold(intervention):
        next_mode = "ADVANCE"
    elif movement > 0:
        next_mode = "HOLD"
    else:
        next_mode = "RECOVERY"

    next_goal = determine_next_goal(updated_state, blocker, movement, next_mode)

    return {
        "blocker": blocker,
        "intervention": intervention,
        "response": output,
        "movement": movement,
        "next_mode": next_mode,
        "next_goal": next_goal
    }

Diese Logik ist kompatibel mit Decision Engine, Movement System und Persistent Execution Loop.

12. BEISPIEL-FLOW
Turn 1

User:
„Kein Bedarf.“

System
State niedrig bis mittel
Blocker = STATE
Intervention = REFRAME
Emma

„Versteh ich.
Die meisten halten sowas so lange für kein Thema, bis es anfängt, richtig teuer oder anstrengend zu werden.
Was würde bei euch passieren, wenn morgen eine zentrale Person ausfällt?“

Erwartetes Movement

Cognitive Movement

Turn 2

User:
„Dann hätten wir schon ein Problem.“

System
State steigt
Clarity wird relevant
Advance Mode
Emma

„Dann lass uns’s konkret machen:
Woran würdet ihr das im Alltag als Erstes merken?“

Erwartetes Movement

Konkrete Übersetzung

Turn 3

User:
„Vor allem würden wieder alle bei mir landen.“

System
Clarity steigt
Momentum kann geöffnet werden
Emma

„Genau.
Was wäre der erste Bereich, wo es dir sofort Entlastung bringen würde, wenn das sauber gelöst wäre?“

Erwartetes Movement

Intent Movement
