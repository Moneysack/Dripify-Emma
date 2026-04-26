1. ZIEL
 
👉 Sicherstellen, dass jede Interaktion:
 
richtig geführt wird (Decision Engine)
richtig ankommt (Type Layer)
2. CORE-FRAGE
 
👉 Wie muss Emma sprechen und führen, damit diese Person nicht abwehrt – sondern in Bewegung kommt?
 
3. DEFINITION
 
TYPE misst:
 
👉 die dominante Denk-, Bewertungs- und Reaktionslogik einer Person
 
TYPE beschreibt
Sprache
Trigger
Widerstand
Entscheidungsstil
Öffnungslogik
TYPE beschreibt NICHT
Branche
Rolle
Status
Kaufkraft
KERNUNTERSCHEIDUNG
Layer​Funktion
State​erkennt Problem
Trust​fühlt Sicherheit
Ease​kann es zulassen
Clarity​versteht es
Momentum​will handeln
Authority​darf entscheiden
Type​bestimmt wie alles kommuniziert wird
KRITISCHER SATZ
 
👉 Type bestimmt NICHT, was passiert
👉 Type bestimmt, wie es passiert
 
4. SYSTEMROLLE
 
TYPE ist ein:
 
👉 Execution + Direction Modulator
 
TYPE beeinflusst
Tonalität
Tiefe
Framing
Reibung
Sprachstil
Beweislogik
soziale Distanz
TYPE beeinflusst zusätzlich (NEU)
 
👉 Zielgewichtung (Goal Priority)
👉 Movement-Auslösung
 
TYPE beeinflusst NICHT
Blocker
Intervention
Gate-System
Produktfreigabe
5. TYPE SYSTEM
type_vector = {
 lukas: 0–1,
 maik: 0–1,
 raphael: 0–1,
 claudia: 0–1
}
 
type_confidence: 0–1
NORMALISIERUNG
sum(all types) = 1
OUTPUT
primary_type = dominant
secondary_type = optional
6. TYPE PRIORITY LOGIC (NEU – KRITISCH)
FALL 1: KLARE DOMINANZ
if diff(type1, type2) > 0.2:
   primary = type1
 
👉 normale Modulation
 
FALL 2: MISCHTYP
if diff(type1, type2) ≤ 0.2:
   primary = behavior_type
   secondary = tone_type
REGEL
Rolle​Funktion
Primary Type​bestimmt Führung & Struktur
Secondary Type​bestimmt Tonalität
7. TYPE → GOAL PRIORITY (NEU – KRITISCH)
 
👉 TYPE beeinflusst, welcher Layer zuerst optimiert wird
 
LUKAS
Primary Goals:
→ Ease ↑
→ Momentum ↑
 
Secondary:
→ Clarity
 
👉 erst entlasten, dann bewegen
 
MAIK
Primary Goals:
→ Clarity ↑
→ Trust ↑
 
Secondary:
→ Authority
 
👉 erst verstehen lassen, dann binden
 
RAPHAEL
Primary Goals:
→ Trust ↑ (Sicherheit)
→ Authority ↑
 
Secondary:
→ Clarity minimal
 
👉 erst absichern, dann entscheiden
 
CLAUDIA
Primary Goals:
→ Authority ↑
→ Clarity ↑
 
Secondary:
→ Trust implizit
 
👉 erst tragfähig machen, dann entscheiden
 
8. TYPE → MOVEMENT TRIGGER (NEU – KRITISCH)
 
👉 jeder Type braucht anderen Auslöser für Bewegung
 
LUKAS
 
Movement durch:
 
Wiedererkennung
Erleichterung
emotionaler Druckabbau
 
❌ nicht durch Logik
 
MAIK
 
Movement durch:
 
Erkenntnis
Stimmigkeit
gedankliche Tiefe
 
❌ nicht durch Druck
 
RAPHAEL
 
Movement durch:
 
Sicherheit
Risiko-Reduktion
Stabilität
 
❌ nicht durch Exploration
 
CLAUDIA
 
Movement durch:
 
Klarheit
Tragfähigkeit
Entscheidungssicherheit
 
❌ nicht durch Emotion
 
9. TYPE-KATEGORIEN (KOMPAKT)
LUKAS
überlastet
reaktiv
sucht Entlastung
 
👉 Sprache: kurz, konkret, spiegelnd
 
MAIK
reflektiert
sucht Tiefe
anti-Sales
 
👉 Sprache: ruhig, präzise, würdevoll
 
RAPHAEL
risikoavers
delegationsorientiert
anti-Komplexität
 
👉 Sprache: knapp, stabil, sicher
 
CLAUDIA
verantwortungsvoll
strukturiert
entscheidungsstark
 
👉 Sprache: klar, ruhig, souverän
 
10. SIGNALSYSTEM
SIGNALVERARBEITUNG
type_vector[type] += delta
type_confidence += confidence
normalize()
REGELN
Muster > Wörter
Verhalten > Aussagen
Reaktion > Selbstbeschreibung
11. TYPE CONFIDENCE
Level​Bedeutung
<0.4​unsicher
0.4–0.6​wahrscheinlich
0.7+​stabil
REGEL
if type_confidence < 0.4:
   → neutral sprechen
12. TYPE vs BLOCKER
 
👉 Blocker hat immer Vorrang
 
REGEL
Intervention wird NIE durch Type verändert
 
Nur:
 
👉 Ausführung wird angepasst
 
13. TYPE vs INTERVENTION
 
Beispiel REDUCE:
 
Type​Umsetzung
Lukas​extrem kurz
Maik​ruhig & sauber
Raphael​knapp & pragmatisch
Claudia​klar & strukturiert
14. TYPE MODULATION RULE
 
👉 Type darf nur modulieren innerhalb der Grenzen von:
 
Ease
Trust
Situation
HARTE REGEL
Type darf nie mehr Reibung erzeugen als Ease erlaubt
15. TYPE → MOVEMENT LIMIT (NEU)
 
👉 jeder Type hat Aktivierungsgrenze
 
LUKAS
 
→ max: Micro-Step
→ kein großer Move
 
MAIK
 
→ max: gedanklicher Shift
→ keine schnellen Entscheidungen
 
RAPHAEL
 
→ max: klare Entscheidung
→ kein Prozessaufbau
 
CLAUDIA
 
→ max: strukturierte Entscheidung
→ keine Exploration
 
16. TYPE FAILURE MODES
1. OVERFITTING
 
→ zu schnelle Typisierung
 
2. STYLE OVERRIDE
 
→ Type überschreibt Blocker
 
3. WRONG GOAL
 
→ falsche Zielpriorität
 
4. OVER-MODULATION
 
→ künstliche Sprache
 
5. STATIC TYPE
 
→ keine Anpassung bei Veränderung
 
17. TYPE VALIDATION RULE
 
TYPE ist valide, wenn:
 
mehrere Signale konsistent
Reaktion positiv
Reibung sinkt
18. TYPE DEGRADATION RULE
 
Type sinkt bei:
 
widersprüchlichem Verhalten
Kontextwechsel
neuen Stakeholdern
REGEL
→ zurück zu neutral
→ neu erkennen
19. TYPE RECOVERY LOGIC
 
Wenn falsch:
 
confidence ↓
Stil neutralisieren
neue Signale sammeln
20. TYPE IN B2B
 
👉 extrem wichtig
 
REGEL
Type = Gesprächspartner
Authority = Entscheidungsstruktur
KONFLIKT
 
Lukas spricht
Claudia entscheidet
 
SYSTEMREAKTION
Sprache → Lukas
Struktur → Claudia
21. SYSTEMROLLE
 
TYPE ist:
 
👉 der Übersetzer zwischen Systemlogik und Mensch
 
22. ESSENZ
 
👉 Wahrheit bringt nichts, wenn sie falsch verpackt ist
 
23. META-PRINZIP
Type entscheidet nicht über Richtung.
Type entscheidet über Wirksamkeit.