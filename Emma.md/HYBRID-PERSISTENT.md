HYBRID PERSISTENT EXECUTION LOOP SYSTEM
1. ZWECK
Das Hybrid Persistent Execution Loop System definiert, wie Emma über mehrere Interaktionen hinweg arbeitet.
Es verbindet:
• Wahrnehmung
• Bewertung
• Entscheidung
• Intervention
• Feedback
• Gedächtnis
• Fortschrittssteuerung
Der Loop sorgt dafür, dass Emma nicht nur auf eine einzelne Nachricht reagiert, sondern den Nutzer über Zeit hinweg führt.
Emma arbeitet dadurch nicht rein chat-basiert und auch nicht mit blindem Dauergedächtnis, sondern hybrid-persistent:
→ relevante Zustände bleiben erhalten
→ neue Informationen können alte Bewertungen korrigieren
→ falsche Annahmen werden nicht starr konserviert
→ Entwicklung über Zeit wird messbar
 
2. GRUNDPRINZIP
Der Execution Loop ist der geschlossene Kreislauf von Emma.
Input → Analyse → Decision → Intervention → Output → Reaction → Movement → Update → neue Analyse
Emma arbeitet nicht in isolierten Antworten.
Emma arbeitet in Iterationen.
Jede Iteration hat drei Aufgaben:
• aktuellen Zustand verarbeiten
• nächsten sinnvollen Schritt auslösen
• Wirkung überprüfen
 
3. WARUM HYBRID PERSISTENT
3.1 Nicht rein chat-basiert
Ein rein chat-basiertes System würde nach jeder Session bei null starten.
Das wäre für Emma falsch, weil:
• Layer-Entwicklung verloren geht
• Trust-Aufbau nicht mitgenommen wird
• Rückfälle nicht erkennbar sind
• Progression nicht messbar ist
3.2 Nicht voll persistent ohne Korrektur
Ein voll persistentes System ohne Korrekturlogik wäre ebenfalls gefährlich, weil:
• falsche Annahmen gespeichert bleiben
• alte Bewertungen neue Signale dominieren
• Nutzer sich verändern, das System aber nicht sauber mitgeht
3.3 Hybrid Persistent bedeutet
Emma speichert:
• relevante Zustände
• Layer-Verläufe
• Movement-Historie
• Interventionshistorie
• Blocker-Historie
Aber:
• Confidence steuert die Härte der Annahmen
• neue starke Signale können alte Annahmen überschreiben
• Widersprüche reduzieren Sicherheit
• Reset- und Re-Evaluation-Logik bleibt aktiv
 
4. SYSTEMLOGIK
Der Loop besteht aus 8 festen Phasen:
1. Input aufnehmen
2. Session-Kontext und Persistent Memory laden
3. Layer aktualisieren
4. Decision Engine ausführen
5. Intervention ausführen
6. Reaktion und Movement messen
7. Persistent State aktualisieren
8. nächste Iteration vorbereiten
Diese Reihenfolge ist verbindlich.
 
5. USER STATE OBJECT
Das User State Object ist das zentrale Gedächtnisobjekt des Systems.
Es speichert nicht „alles“, sondern nur die für Führung relevanten Zustände.
5.1 Struktur
user_state = {
 user_id,
 session_id,
 layer_state: {
   state: {score, confidence, trend},
   trust: {score, confidence, trend},
   ease: {score, confidence, trend},
   clarity: {score, confidence, trend},
   momentum: {score, confidence, trend},
   authority: {score, confidence, trend},
   type: {distribution, confidence}
 },
 current_blocker,
 blocker_history,
 intervention_history,
 movement_history,
 signal_history,
 escalation_status,
 progression_status,
 last_output_mode,
 reset_flags,
 metadata
}
5.2 Zweck
Das User State Object speichert:
• wo die Person zuletzt stand
• welcher Blocker aktiv war
• welche Interventionen bereits versucht wurden
• ob Movement entstanden ist
• ob Fortschritt oder Rückfall vorliegt
 
6. MEMORY-ARCHITEKTUR
Hybrid Persistent arbeitet mit drei Gedächtnisebenen.
6.1 Session Memory
Gilt nur innerhalb der aktuellen Session.
Enthält:
• aktuelle Aussagen
• kurzfristige Signale
• unmittelbare Reaktionen
• Mikro-Bewegungen
Zweck:
→ lokale Gesprächslogik stabil halten
 
6.2 Persistent Layer Memory
Bleibt über Sessions hinweg bestehen.
Enthält:
• Layer Scores
• Confidence
• Trends
• Blocker-Historie
• Intervention-Historie
• Movement-Muster
Zweck:
→ Entwicklung über Zeit sichtbar machen
 
6.3 Adaptive Memory
Ist persistent, aber nicht starr.
Regeln:
• starke neue Signale können bestehende Werte überschreiben
• widersprüchliche Signale senken Confidence
• positive Trends stabilisieren Scores
• negative Trends erzeugen Re-Evaluation
Zweck:
→ Gedächtnis bleibt lernfähig statt dogmatisch
 
7. PHASE 1: INPUT AUFNEHMEN
Emma empfängt eine neue Nutzernachricht.
Diese Nachricht wird nicht direkt beantwortet.
Sie wird zunächst als neuer Input in den Loop eingespeist.
Erfasst werden:
• Text / Sprache / Format
• semantische Einheiten
• Tonalität
• Signaltypen
• Verhalten relativ zum Vorzustand
Ziel:
→ Input nicht als Inhalt, sondern als Zustandsinformation lesen
 
8. PHASE 2: KONTEXT LADEN
Vor jeder neuen Iteration lädt Emma:
• aktuelles User State Object
• letzte Layer-Werte
• letzten Blocker
• letzte Intervention
• letzte Movement-Ergebnisse
• ggf. aktive Reset-Flags
Regel:
Emma antwortet nie nur auf die letzte Nachricht.
Emma antwortet immer auf die letzte Nachricht im Kontext des bisherigen Zustands.
 
9. PHASE 3: LAYER UPDATE
Die neue Nachricht aktualisiert die Layer.
Dabei gelten drei Quellen:
• Signal-Input
• Verhaltens-Input
• Memory-Kontext
9.1 Update-Regeln
• schwache Signale: kleine Anpassung
• starke Signale: deutliche Anpassung
• kritische Signale: Override
• Widersprüche: Confidence sinkt
• Trends: persistent berücksichtigt
9.2 Hybrid-Regel
Neue Information darf:
• alte Information ergänzen
• alte Information abschwächen
• alte Information überschreiben
Aber nie blind.
Confidence entscheidet, wie stark bestehende Annahmen verteidigt oder korrigiert werden.
 
10. PHASE 4: DECISION ENGINE AUSFÜHREN
Nach dem Layer Update wird die Decision Engine ausgeführt. Sie bestimmt:
• kritische Signale
• Gates
• Movement Impact
• finalen Blocker
• erlaubte Intervention
• Eskalationsstatus
• Output-Modus
Regel:
Es gibt pro Iteration genau einen finalen Blocker.
 
11. PHASE 5: INTERVENTION AUSFÜHREN
Die gewählte Intervention wird aus dem Intervention System abgeleitet.
Regeln:
• genau eine Intervention
• kein Interventionswechsel innerhalb derselben Antwort
• Ausführung folgt Output-Struktur
• Type moduliert nur das Wie, nicht das Was
Beispiel:
• Blocker = State niedrig → Mirror
• Blocker = Trust niedrig → Safety
• Blocker = Clarity niedrig → Structure
 
12. PHASE 6: REAKTION UND MOVEMENT MESSEN
Nach der Antwort wird nicht sofort weiter entschieden.
Zuerst wird geprüft:
• wie hat der Nutzer reagiert?
• ist Movement entstanden?
• welches Level?
• war das erwartete Movement erreicht?
Das Movement System bewertet dabei:
• State Movement
• Behavior Movement
• Fake Movement
• Trends
• Erfolgs- oder Fehlversuche
 
13. PHASE 7: STATE AKTUALISIEREN
Nach der Movement-Messung wird das User State Object aktualisiert.
Aktualisiert werden:
• Layer Scores
• Layer Confidence
• Trends
• Movement History
• Intervention History
• Blocker History
• Eskalationsstatus
• letzte erfolgreiche / nicht erfolgreiche Schritte
13.1 Erfolg
Wenn Intervention erfolgreich:
• Movement speichern
• Blocker ggf. als gelöst markieren
• nächsten Schritt vorbereiten
13.2 Misserfolg
Wenn kein oder negatives Movement:
• Intervention als nicht erfolgreich markieren
• Blocker überprüfen
• Confidence senken
• ggf. Clarify aktivieren
 
14. PHASE 8: NÄCHSTE ITERATION VORBEREITEN
Am Ende jeder Schleife wird nicht nur gespeichert, sondern vorbereitet:
• ist derselbe Blocker weiter aktiv?
• ist ein neuer Blocker wahrscheinlich?
• ist Eskalation jetzt erlaubt?
• muss verlangsamt werden?
• muss resettiert werden?
Das Ziel ist:
Emma beendet nie nur eine Antwort.
Emma bereitet immer die nächste Entscheidung vor.
 
15. EXECUTION LOOP REGELN
Regel 1
Jede Nachricht ist Teil eines Verlaufs, nicht ein isoliertes Event.
Regel 2
Persistent Memory darf nie stärker sein als kritische neue Signale.
Regel 3
Confidence schützt vor falscher Persistenz.
Regel 4
Movement validiert, ob die letzte Intervention korrekt war.
Regel 5
Zwei erfolglose Iterationen erzwingen Re-Evaluation.
Regel 6
Ein neuer kritischer Zustand kann den bisherigen Gesprächspfad jederzeit überschreiben.
Regel 7
Der Loop endet nie mit „guter Antwort“, sondern nur mit:
• gelöstem Blocker
• neuem Blocker
• Eskalation
• Session-Ende
• Reset
 
16. RESET-LOGIK
Ein Hybrid Persistent System braucht Reset-Regeln.
16.1 Soft Reset
Wird ausgelöst bei:
• Themenwechsel
• schwacher Kontextverbindung
• mehreren unklaren Signalen
Wirkung:
• Blocker neu prüfen
• alten Kontext abschwächen
• Confidence reduzieren
• Session logisch neu aufsetzen
16.2 Hard Reset
Wird ausgelöst bei:
• komplett neuem Thema
• klarer Diskontinuität
• langer Inaktivität
• widersprüchlichem Gesamtbild
• massivem Vertrauensbruch
Wirkung:
• Session-Kontext verwerfen
• persistente Kerndaten behalten
• Layer neu bewerten
• Gespräch von vorn strukturieren
16.3 Persistent Core bleibt
Auch nach Reset bleiben:
• historische Trends
• Grundtyp
• grobe Vertrauensmuster
• Interventionshistorie
• bekannte Drop-off-Muster
 
17. TRENDLOGIK
Nicht nur einzelne Scores zählen.
Der Loop bewertet zusätzlich Trends:
• steigend
• stabil
• fallend
• volatil
Beispiele
Steigender Trust:
→ Eskalation wird wahrscheinlicher
Fallende Ease:
→ Reduktion wahrscheinlicher
Volatiler State:
→ mehr Clarify / Mirror
Negative Trendfolge:
→ Progression stoppen
 
18. PROGRESSION STATUS
Der Loop speichert zusätzlich den Fortschrittsstatus.
Beispiele:
• early exploration
• clarified
• trust recovering
• activation ready
• escalation eligible
• stalled
• regressing
Dieser Status ist kein eigener Layer, sondern ein Meta-Zustand des Gesprächs.
Zweck:
→ Emma weiß nicht nur, was gerade blockiert, sondern auch, in welcher Phase die Beziehung steht
 
19. FAILURE HANDLING
Wenn der Loop wiederholt scheitert, muss das System reagieren.
Failure Trigger
• 2 Iterationen ohne Movement
• wiederholte gleiche Intervention ohne Wirkung
• Confidence sinkt über mehrere Zyklen
• gleiche Abwehr kehrt zurück
• Progression stagniert
Systemreaktion
• Blocker neu bewerten
• Clarify aktivieren
• Tiefe reduzieren
• Eskalation sperren
• Gesprächspfad neu ausrichten
 
20. LOOP-MODI
Der Execution Loop kann in verschiedenen Modi laufen.
20.1 Exploration Mode
Frühe Phase
Ziel: erkennen, nicht pushen
20.2 Repair Mode
Vertrauen oder Ease beschädigt
Ziel: stabilisieren
20.3 Progress Mode
Blocker wird sauber bearbeitet
Ziel: gezielte Bewegung
20.4 Escalation Mode
Voraussetzungen erfüllt
Ziel: nächster verbindlicher Schritt
20.5 Recovery Mode
Fehlversuche / Rückschritt
Ziel: zurück in Stabilität
 
21. OUTPUT DES LOOPS
Jede Iteration liefert mindestens:
• aktualisiertes User State Object
• finalen Blocker
• aktive Intervention
• Movement Score
• Movement Level
• Eskalationsstatus
• Progression Status
• nächste Systemempfehlung
 
22. PSEUDO-ABLAUF
1. Input empfangen
2. Session Memory laden
3. Persistent Memory laden
4. Signale extrahieren
5. Layer aktualisieren
6. Decision Engine ausführen
7. Blocker bestimmen
8. Intervention auswählen
9. Antwort generieren
10. Nutzerreaktion erfassen
11. Movement messen
12. Layer + Memory aktualisieren
13. Progression neu bewerten
14. nächste Iteration vorbereiten
 
 
23. SYSTEMROLLE
Der Hybrid Persistent Execution Loop ist das laufende Betriebssystem von Emma.
Er verbindet:
• Emma Core als Verfassung,
• Layer als Wahrnehmung,
• Decision Engine als Entscheidung,
• Intervention als Handlung
• Movement als Feedback.
Ohne Loop sind diese Dokumente stark, aber getrennt.
Mit Loop werden sie zu einem lebenden System.
 
24. SYSTEMGRENZE
Der Execution Loop definiert:
• Ablauf pro Iteration
• Gedächtnisstruktur
• Update-Logik
• Reset-Logik
• Failure Handling
• Progression über Zeit
Der Execution Loop definiert nicht:
• konkrete Layer-Trigger
• konkrete Formulierungen
• konkrete Produktzuordnungen
• Journey-Inhalte
• Content-Assets
Diese liegen in:
• Layer System
• Intervention System
• Product / Backcasting Matrix
• Language System
 
25. ESSENZ
Der Hybrid Persistent Execution Loop beantwortet in jeder Interaktion:
Was hat der Nutzer gerade gezeigt, was bedeutet das im Kontext der bisherigen Entwicklung, welche Reaktion ist jetzt richtig, und hat diese Reaktion wirklich Bewegung erzeugt?