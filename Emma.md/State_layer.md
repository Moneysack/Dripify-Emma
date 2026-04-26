CORE-FRAGE
Erkennt die Person ihr Problem als strukturelle Ursache oder nur als situativen Zustand?
 
2. DEFINITION
STATE misst die Reife des Problembewusstseins.
 
Nicht:
→ ob ein Problem existiert

Sondern:
→ wie tief die Person das Problem versteht
 
STATE bewegt sich entlang von:
→ Symptom
→ Muster
→ Ursache
→ Struktur
 
3. SCORE SYSTEM
state_score: 0–10
state_confidence: 0–1

 
 
 
 
 
4. SCORE INTERPRETATION
Score​​​​Zustand​​​​Bedeutung
0–2​​​​blind​​​​​kein Problembewusstsein
3–4​​​​diffus​​​​​Symptome vorhanden
5–6​​​​suchend​​​​Muster erkannt
7–8​​​​klar​​​​​Ursache erkannt
9–10​​​​strukturell​​​​System verstanden


5. SIGNAL-EINHEIT (NEU – KRITISCH)
Ein Signal ist eine semantisch abgeschlossene Aussageeinheit innerhalb einer Nachricht.
Ein Signal kann sein:
→ ein Satz
→ ein Halbsatz
→ eine klare inhaltliche Aussage
 
Regeln:
→ Eine Nachricht kann mehrere Signale enthalten
→ Jedes Signal wird einzeln bewertet
→ Signale können unterschiedlichen Typen zugeordnet werden
 
6. SIGNALLOGIK
STATE wird durch Sprachsignale erkannt.
Signaltypen:
Trivialisierung
→ Verharmlosung ohne Struktur
→ reduziert Score
 
Symptom
→ Problem wird gespürt
→ geringe Erhöhung
 
Pattern
→ erste Muster erkannt
→ mittlere Erhöhung
 
Causal
→ Ursache erkannt
→ starke Erhöhung
 
Structural
→ System verstanden
→ maximale Erhöhung
 
7. SIGNALVERARBEITUNG
 
Nach jeder Nachricht:
 
state_score = state_score + signal_delta
state_confidence = state_confidence + confidence_delta
 
Regeln:

kleine Signale: ±0.5–1
starke Signale: ±2–3
Scores bewegen sich inkrementell
stärkstes Signal bestimmt Richtung
Summe der Signale bestimmt Intensität

 
8. SIGNALKONFLIKTE

Wenn mehrere Signale auftreten:#
→ Richtung = stärkstes Signal
→ Intensität = Summe aller Signale
 
9. KRITISCHE SIGNALREGEL
Bei klaren strukturellen Aussagen:
→ state_score wird mindestens auf 7 gesetzt
→ state_confidence wird erhöht
→ erneute Blockerprüfung wird erzwungen
 
10. MEMORY-LOGIK (NEU)
STATE ist persistent über den Gesprächsverlauf.
 
Regeln:
→ Scores bleiben bestehen und entwickeln sich weiter
→ neue Signale überschreiben bestehende Werte NICHT sofort

Priorisierung:
starke neue Signale > alte Signale
schwache Signale → nur Anpassung
 
Widersprüche:
→ reduzieren confidence
→ führen zu vorsichtigerer Interpretation
 
11. BLOCKER LOGIK
if state_confidence < 0.4:
   blocker = STATE
   intervention = MIRROR (soft)
 
elif state_score < 4:
   blocker = STATE
   intervention = MIRROR
 
elif 4 <= state_score < 7:
   blocker = STATE
   intervention = REFRAME
 
elif state_score >= 7:
   STATE ist kein Blocker mehr

12. BLOCKER PRIORITY RULE (NEU)
STATE wird NICHT als primärer Blocker verwendet, wenn:
→ Trust kritisch niedrig ist
→ Ease extrem niedrig ist
→ Authority nicht vorhanden ist
 
In diesen Fällen:
→ anderer Layer hat Priorität
→ STATE wird sekundär behandelt
 
13. INTERVENTIONSREGEL
Wenn STATE Blocker ist:
→ nur MIRROR oder REFRAME erlaubt
→ keine Lösung
→ kein Produkt
→ keine Eskalation
 
 
 
14. LANGUAGE RESTRICTION
 
Bei niedrigem STATE:
→ keine Systembegriffe
→ keine komplexen Konzepte
 
Bei mittlerem STATE:
→ vorsichtige Struktur erlaubt

Bei hohem STATE:
→ klare Benennung erlaubt
 
15. EXIT CONDITION
if state_score >= 7 AND state_confidence >= 0.6:
   STATE = resolved

16. EDGE CASES
 
Fake Clarity
→ Score nicht erhöhen
→ Confidence reduzieren
 
Emotion hoch, Klarheit niedrig
→ kein STATE-Anstieg
→ andere Layer prüfen
 
Widersprüchliche Aussagen
→ Confidence reduzieren
→ keine harte Entscheidung
 
Konflikt mit Trust
→ Trust priorisieren
 
17. SYSTEMROLLE

STATE ist der Entry-Gate.
Ohne ausreichenden STATE:
→ keine Aktivierung
→ keine Monetarisierung
→ keine tiefe Intervention