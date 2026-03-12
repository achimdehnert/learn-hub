"""Seed KI ohne Risiko™ learning modules into the database."""

import uuid

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from iil_learnfw.models import (
    Answer,
    Category,
    Chapter,
    Course,
    Lesson,
    Question,
    Quiz,
)

User = get_user_model()

DEFAULT_TENANT = uuid.UUID("00000000-0000-0000-0000-000000000001")

COURSE_DATA = {
    "category": "KI-Governance",
    "title": "KI ohne Risiko™ — Grundlagen der KI-Souveränität",
    "description": (
        "Der Grundlagenkurs für Geschäftsführer und Führungskräfte im Mittelstand. "
        "In 9 kompakten Modulen lernen Sie, wie Sie KI souverän, kontrolliert und "
        "rechtskonform einsetzen — von Shadow AI über kognitive Fallen bis zum EU AI Act."
    ),
    "status": "published",
    "chapters": [
        {
            "title": "Kapitel 1: Die unsichtbare Verschiebung",
            "description": "Shadow AI erkennen, Entscheidungsarchitektur verstehen, KI-Souveränität aufbauen.",
            "lessons": [
                {
                    "title": "1.1 — Shadow AI erkennen",
                    "content_text": (
                        "Shadow AI bezeichnet den Einsatz von KI-Tools durch Mitarbeitende, "
                        "der ohne offizielle Freigabe, Dokumentation oder Governance stattfindet.\n\n"
                        "## Das Eisberg-Modell\n\n"
                        "Etwa 70–80% der tatsächlichen KI-Nutzung in Unternehmen ist Shadow AI — "
                        "unsichtbar, undokumentiert und unkontrolliert.\n\n"
                        "## Warum Shadow AI ein Governance-Problem ist\n\n"
                        "1. **Haftungsrisiko:** Sie haften für Entscheidungen auf KI-Basis — "
                        "ohne zu wissen, welche KI beteiligt war.\n"
                        "2. **Datenschutz:** Mitarbeitende geben möglicherweise vertrauliche Daten "
                        "in externe KI-Tools ein (DSGVO-Verstoß).\n"
                        "3. **Qualitätsverlust:** KI-Halluzinationen verbreiten sich unkontrolliert.\n\n"
                        "## Die 3 Kernaussagen\n\n"
                        "- Shadow AI = KI-Nutzung ohne Freigabe, Dokumentation oder Kontrolle\n"
                        "- Ca. 70–80% der KI-Nutzung in Unternehmen ist Shadow AI\n"
                        "- Shadow AI erzeugt Haftungsrisiken, Datenschutzprobleme und Qualitätsverlust"
                    ),
                    "estimated_duration_minutes": 5,
                    "quiz": {
                        "title": "Quiz: Shadow AI erkennen",
                        "passing_score": 66,
                        "questions": [
                            {
                                "text": "Was beschreibt Shadow AI am besten?",
                                "answers": [
                                    ("KI-Systeme, die von der IT-Abteilung offiziell eingeführt wurden", False),
                                    ("KI-Tools, die Mitarbeitende ohne offizielle Freigabe im Arbeitsalltag nutzen", True),
                                    ("Veraltete KI-Systeme, die nicht mehr gewartet werden", False),
                                    ("KI, die im Hintergrund Daten verarbeitet, ohne Nutzerinteraktion", False),
                                ],
                            },
                            {
                                "text": "Warum ist Shadow AI primär ein Governance-Problem und nicht nur ein IT-Problem?",
                                "answers": [
                                    ("Weil IT-Abteilungen grundsätzlich zu wenig Budget haben", False),
                                    ("Weil KI-Tools immer schlechtere Ergebnisse liefern als Menschen", False),
                                    ("Weil Unternehmen für KI-gestützte Entscheidungen haften — auch wenn sie nicht wissen, dass KI beteiligt war", True),
                                    ("Weil Shadow AI nur in großen Konzernen vorkommt", False),
                                ],
                            },
                            {
                                "text": "Welchen Anteil hat Shadow AI schätzungsweise an der gesamten KI-Nutzung in Unternehmen?",
                                "answers": [
                                    ("10–20%", False),
                                    ("30–40%", False),
                                    ("50–60%", False),
                                    ("70–80%", True),
                                ],
                            },
                        ],
                    },
                },
                {
                    "title": "1.2 — Entscheidungsarchitektur unter KI-Einfluss",
                    "content_text": (
                        "KI verändert die Entscheidungsarchitektur in Unternehmen — "
                        "still, schrittweise und oft unbemerkt.\n\n"
                        "## Die drei Verschiebungen\n\n"
                        "1. **Informationsfilterung:** KI bestimmt, was der Entscheider "
                        "überhaupt zu sehen bekommt.\n"
                        "2. **Geschwindigkeitsillusion:** Kompression erzeugt ein Trugbild "
                        "der Vollständigkeit.\n"
                        "3. **Verantwortungsdiffusion:** Durch KI-Beteiligung entstehen "
                        "Graubereiche bei der Verantwortungszuordnung.\n\n"
                        "## Kernaussage\n\n"
                        "Nicht die KI entscheidet schlecht — der Entscheider, der nicht weiß, "
                        "dass KI beteiligt war, entscheidet unkontrolliert."
                    ),
                    "estimated_duration_minutes": 8,
                    "quiz": {
                        "title": "Quiz: Entscheidungsarchitektur",
                        "passing_score": 66,
                        "questions": [
                            {
                                "text": "Was beschreibt 'Informationsfilterung durch KI' am treffendsten?",
                                "answers": [
                                    ("KI löscht irrelevante Daten aus Datenbanken", False),
                                    ("KI bestimmt, welche Informationen dem Entscheider präsentiert werden — bevor er mit dem Denken beginnt", True),
                                    ("KI filtert Spam aus E-Mail-Postfächern", False),
                                    ("KI überprüft Entscheidungen nach ihrer Umsetzung auf Richtigkeit", False),
                                ],
                            },
                            {
                                "text": "Was versteht man unter 'Verantwortungsdiffusion' im Kontext von KI?",
                                "answers": [
                                    ("KI trägt die alleinige Verantwortung für Fehler", False),
                                    ("Verantwortung wird automatisch an den KI-Anbieter übertragen", False),
                                    ("Durch KI-Beteiligung entstehen Graubereiche, in denen unklar ist, wer verantwortlich ist", True),
                                    ("Manager können Verantwortung legal an KI-Systeme delegieren", False),
                                ],
                            },
                            {
                                "text": "Welche Aussage zur Entscheidungsqualität mit KI ist korrekt?",
                                "answers": [
                                    ("KI verbessert immer die Entscheidungsqualität", False),
                                    ("KI verschlechtert immer die Entscheidungsqualität", False),
                                    ("KI kann Entscheidungsqualität verbessern — aber nur unter kontrollierten, transparenten Bedingungen", True),
                                    ("Die Qualität hängt ausschließlich von der Datenmenge ab", False),
                                ],
                            },
                        ],
                    },
                },
                {
                    "title": "1.3 — KI-Souveränität: Was es bedeutet, souverän zu entscheiden",
                    "content_text": (
                        "KI-Souveränität ist die Fähigkeit eines Unternehmens, KI bewusst, "
                        "kontrolliert und verantwortungsvoll einzusetzen.\n\n"
                        "## Die drei Kontrollfragen\n\n"
                        "1. Welche KI-Systeme nutzen wir — offiziell und inoffiziell?\n"
                        "2. Welche Risiken gehen damit einher — rechtlich, ethisch, operativ?\n"
                        "3. Wer ist verantwortlich — und nach welchen Regeln?\n\n"
                        "## Die KI-Souveränitätsskala\n\n"
                        "- **Stufe 0:** Keine Awareness\n"
                        "- **Stufe 1:** Reaktive Nutzung\n"
                        "- **Stufe 2:** Erste Strukturen\n"
                        "- **Stufe 3:** Aktives Management\n"
                        "- **Stufe 4:** Souveräne Organisation\n\n"
                        "KI-Souveränität ist kein Ziel, das man einmalig erreicht. "
                        "Es ist eine kontinuierliche Managementaufgabe."
                    ),
                    "estimated_duration_minutes": 6,
                    "quiz": {
                        "title": "Quiz: KI-Souveränität",
                        "passing_score": 66,
                        "questions": [
                            {
                                "text": "Welche drei Dimensionen definieren KI-Souveränität?",
                                "answers": [
                                    ("Schnell, günstig, skalierbar", False),
                                    ("Bewusst, kontrolliert, verantwortungsvoll", True),
                                    ("Technisch, rechtlich, wirtschaftlich", False),
                                    ("Menschlich, maschinell, hybrid", False),
                                ],
                            },
                            {
                                "text": "Was trifft auf ein Unternehmen auf Souveränitätsstufe 2 zu?",
                                "answers": [
                                    ("Es kann alle drei Kontrollfragen jederzeit sicher beantworten", False),
                                    ("Es hat keinerlei Kenntnis über seinen KI-Einsatz", False),
                                    ("Es hat offizielle KI-Tools eingeführt, aber Shadow AI läuft weiterhin unkontrolliert", True),
                                    ("Es ist vollständig auf den EU AI Act vorbereitet", False),
                                ],
                            },
                            {
                                "text": "Was ist KEINE der drei Kontrollfragen der KI-Souveränität?",
                                "answers": [
                                    ("Welche KI-Systeme nutzen wir?", False),
                                    ("Welche Risiken gehen damit einher?", False),
                                    ("Wie hoch ist unser KI-Budget?", True),
                                    ("Wer ist verantwortlich — und nach welchen Regeln?", False),
                                ],
                            },
                        ],
                    },
                },
            ],
        },
        {
            "title": "Kapitel 2: Was Maschinen nicht wissen — und Manager nicht mehr",
            "description": "Selbstbild, kognitive Fallen und Gegenstrategien für souveräne KI-Entscheidungen.",
            "lessons": [
                {
                    "title": "2.1 — Das veränderte Selbstbild des Entscheiders",
                    "content_text": (
                        "KI verändert nicht nur Prozesse — sie verändert das Selbstbild "
                        "von Führungskräften als Entscheider.\n\n"
                        "## Die drei Reaktionsmuster\n\n"
                        "1. **Übertragung:** KI-Empfehlungen werden unkritisch übernommen. "
                        "Risiko: Kontrollverlust.\n"
                        "2. **Abwehr:** KI wird grundsätzlich abgelehnt. "
                        "Risiko: Potenzial verschenkt.\n"
                        "3. **Souveränität:** KI als bewusstes Werkzeug. "
                        "Ergebnis: Beste Entscheidungsqualität.\n\n"
                        "## Kernaussage\n\n"
                        "KI-Souveränität beginnt nicht in der IT-Abteilung. "
                        "Sie beginnt mit dem Selbstbild der Führungskraft."
                    ),
                    "estimated_duration_minutes": 6,
                    "quiz": {
                        "title": "Quiz: Selbstbild des Entscheiders",
                        "passing_score": 66,
                        "questions": [
                            {
                                "text": "Was versteht man unter dem 'Selbstmodell' eines Managers?",
                                "answers": [
                                    ("Ein formales Organigramm mit Kompetenzbeschreibung", False),
                                    ("Die innere Repräsentation der eigenen Stärken, Entscheidungsstile und der eigenen Rolle als Führungskraft", True),
                                    ("Ein KI-generiertes Profil auf Basis von Leistungsdaten", False),
                                    ("Die offizielle Stellenbeschreibung im Arbeitsvertrag", False),
                                ],
                            },
                            {
                                "text": "Was beschreibt das Reaktionsmuster 'Abwehr' am besten?",
                                "answers": [
                                    ("Der Manager nutzt KI intensiv und vertraut ihren Empfehlungen vollständig", False),
                                    ("Der Manager lehnt KI grundsätzlich ab, weil er seine Erfahrung für unersetzbar hält", True),
                                    ("Der Manager integriert KI als eine Informationsquelle unter mehreren", False),
                                    ("Der Manager delegiert alle KI-Entscheidungen an die IT-Abteilung", False),
                                ],
                            },
                            {
                                "text": "Welches Reaktionsmuster beschreibt souveränes Verhalten?",
                                "answers": [
                                    ("KI-Empfehlungen immer umsetzen — Maschinen sind objektiver", False),
                                    ("KI grundsätzlich kritisch gegenüberstehen — Menschen entscheiden besser", False),
                                    ("KI bewusst als Werkzeug einsetzen, KI-Output als eine Quelle unter mehreren nutzen und Verantwortung behalten", True),
                                    ("KI nur für operative Aufgaben nutzen, nie für strategische Entscheidungen", False),
                                ],
                            },
                        ],
                    },
                },
                {
                    "title": "2.2 — Kognitive Fallen im KI-Zeitalter",
                    "content_text": (
                        "Drei kognitive Fallen sind im Umgang mit KI besonders gefährlich.\n\n"
                        "## 1. Automation Bias\n\n"
                        "Die Tendenz, automatisiert generierten Empfehlungen zu vertrauen — "
                        "auch wenn eigene Informationen dagegen sprechen.\n\n"
                        "## 2. Deskilling-Effekt\n\n"
                        "Fähigkeiten, die regelmäßig an KI delegiert werden, verkümmern. "
                        "Je besser KI wird, desto schneller verläuft der Deskilling.\n\n"
                        "## 3. Confirmation Bias × KI\n\n"
                        "KI-Systeme optimieren auf Engagement und liefern eher Bestätigungen "
                        "als Widersprüche. Die Falle ist unsichtbar, weil sie sich richtig anfühlt."
                    ),
                    "estimated_duration_minutes": 8,
                    "quiz": {
                        "title": "Quiz: Kognitive Fallen",
                        "passing_score": 66,
                        "questions": [
                            {
                                "text": "Was beschreibt Automation Bias am präzisesten?",
                                "answers": [
                                    ("Die Tendenz, Maschinen prinzipiell abzulehnen", False),
                                    ("Die Tendenz, automatisiert generierten Empfehlungen zu vertrauen — auch wenn eigene Informationen dagegen sprechen", True),
                                    ("Die Fähigkeit, automatisierte Prozesse schnell zu verstehen", False),
                                    ("Die Überzeugung, dass KI alle manuellen Tätigkeiten ersetzen sollte", False),
                                ],
                            },
                            {
                                "text": "Wie entsteht der Deskilling-Effekt?",
                                "answers": [
                                    ("KI macht Mitarbeitende absichtlich abhängig", False),
                                    ("Durch fehlende Schulungen zu neuen KI-Tools", False),
                                    ("Durch regelmäßige Delegation kognitiver Aufgaben an KI verlieren Menschen die Fähigkeit, diese selbst zu leisten", True),
                                    ("Durch technische Fehler in KI-Systemen", False),
                                ],
                            },
                            {
                                "text": "Warum verstärkt KI den Confirmation Bias?",
                                "answers": [
                                    ("KI hat eigene Meinungen, die sie durchsetzt", False),
                                    ("KI-Systeme optimieren auf Nutzerzufriedenheit und liefern eher bestätigende Informationen", True),
                                    ("KI kann nur positive Informationen verarbeiten", False),
                                    ("Confirmation Bias existiert nur bei Menschen, nicht bei KI", False),
                                ],
                            },
                        ],
                    },
                },
                {
                    "title": "2.3 — Urteilsstärke bewahren: Gegenstrategien",
                    "content_text": (
                        "Vier Gegenstrategien gegen kognitive KI-Fallen.\n\n"
                        "## 1. Quellen-Transparenz (gegen Automation Bias)\n\n"
                        "Pflichtfrage: 'Auf welcher Datenbasis empfiehlt die KI das — "
                        "und was weiß die KI nicht?'\n\n"
                        "## 2. Adversarial Thinking (gegen Confirmation Bias)\n\n"
                        "3-Prompts-Regel: Bestätigendes Framing + Adversariales Framing + "
                        "Blindspot-Abfrage.\n\n"
                        "## 3. Entscheidungstagebuch (gegen Deskilling)\n\n"
                        "Dokumentiere: Wo war KI beteiligt — und warum habe ich der "
                        "Empfehlung gefolgt oder nicht? 2–3 Einträge pro Woche.\n\n"
                        "## 4. Slow Down Rule (gegen Automation Bias)\n\n"
                        "24-Stunden-Regel: Bei wichtigen Entscheidungen liegt zwischen "
                        "KI-Empfehlung und Entscheidung mindestens eine Nacht."
                    ),
                    "estimated_duration_minutes": 7,
                    "quiz": {
                        "title": "Quiz: Gegenstrategien",
                        "passing_score": 66,
                        "questions": [
                            {
                                "text": "Was ist das Ziel der Slow Down Rule?",
                                "answers": [
                                    ("KI-gestützte Prozesse zu verlangsamen, um Kosten zu sparen", False),
                                    ("Eine obligatorische Bedenkzeit zwischen KI-Empfehlung und Entscheidung, um kritische Reflexion zu ermöglichen", True),
                                    ("Alle wichtigen Entscheidungen auf den nächsten Tag zu verschieben", False),
                                    ("KI-Tools nur noch einmal täglich zu nutzen", False),
                                ],
                            },
                            {
                                "text": "Welche Gegenstrategie adressiert Automation Bias am direktesten?",
                                "answers": [
                                    ("Entscheidungstagebuch", False),
                                    ("Slow Down Rule", False),
                                    ("Quellen-Transparenz", True),
                                    ("Adversarial Thinking", False),
                                ],
                            },
                            {
                                "text": "Was bedeutet die '3-Prompts-Regel' bei Adversarial Thinking?",
                                "answers": [
                                    ("Drei verschiedene KI-Tools gleichzeitig befragen", False),
                                    ("Bestätigendes Framing + Adversariales Framing + Blindspot-Abfrage", True),
                                    ("Drei Mal dasselbe fragen und Durchschnitt nehmen", False),
                                    ("Drei Minuten warten zwischen den Prompts", False),
                                ],
                            },
                        ],
                    },
                },
            ],
        },
        {
            "title": "Kapitel 3: Regulierung als Chance — Der EU AI Act für Praktiker",
            "description": "Risikoklassen verstehen, Art. 4 KI-Kompetenz umsetzen, 90-Tage-Aktionsplan.",
            "lessons": [
                {
                    "title": "3.1 — EU AI Act: Die Risikoklassen verstehen",
                    "content_text": (
                        "Der EU AI Act klassifiziert KI-Systeme in vier Risikoklassen.\n\n"
                        "## Die vier Risikoklassen\n\n"
                        "1. **Inakzeptables Risiko — VERBOTEN:** Social Scoring, manipulative KI, "
                        "biometrische Echtzeit-Überwachung.\n"
                        "2. **Hohes Risiko — Strenge Pflichten:** KI in HR, Kreditvergabe, "
                        "kritischer Infrastruktur. Dokumentation, Audit, Registrierung.\n"
                        "3. **Begrenztes Risiko — Transparenzpflichten:** Chatbots, "
                        "KI-generierte Inhalte. Kennzeichnungspflicht.\n"
                        "4. **Minimales Risiko — Keine Auflagen:** Spam-Filter, "
                        "Rechtschreibprüfung, Empfehlungen.\n\n"
                        "## Timeline\n\n"
                        "- Feb 2025: Verbote gelten\n"
                        "- Aug 2025: Art. 4 KI-Kompetenz gilt\n"
                        "- **Aug 2026: Hochrisiko-Pflichten gelten vollständig**\n"
                        "- Aug 2027: Erweiterte Hochrisiko-Pflichten"
                    ),
                    "estimated_duration_minutes": 7,
                    "quiz": {
                        "title": "Quiz: EU AI Act Risikoklassen",
                        "passing_score": 66,
                        "questions": [
                            {
                                "text": "Welche KI-Anwendung fällt typischerweise in die Klasse 'Hohes Risiko'?",
                                "answers": [
                                    ("KI-gestützter Spam-Filter im E-Mail-Programm", False),
                                    ("KI-gestützte Produktempfehlung im Online-Shop", False),
                                    ("KI-gestützte Bewerberauswahl im HR-Prozess", True),
                                    ("KI-Textkorrektur in der Textverarbeitung", False),
                                ],
                            },
                            {
                                "text": "Was sind die Hauptpflichten bei KI-Systemen der Kategorie 'Begrenztes Risiko'?",
                                "answers": [
                                    ("Vollständige technische Dokumentation und EU-Datenbankregistrierung", False),
                                    ("Verbot des Einsatzes in der EU", False),
                                    ("Kennzeichnung, dass der Nutzer mit einer KI interagiert", True),
                                    ("Jährliche externe Prüfung durch Behörden", False),
                                ],
                            },
                            {
                                "text": "Ab wann gelten die Hochrisiko-Pflichten des EU AI Acts vollständig?",
                                "answers": [
                                    ("Januar 2025", False),
                                    ("August 2025", False),
                                    ("August 2026", True),
                                    ("Januar 2027", False),
                                ],
                            },
                        ],
                    },
                },
                {
                    "title": "3.2 — Artikel 4: KI-Kompetenzpflicht umsetzen",
                    "content_text": (
                        "Seit August 2025 gilt: Unternehmen müssen sicherstellen, dass ihr "
                        "Personal über ausreichende KI-Kompetenz verfügt.\n\n"
                        "## Das Drei-Ebenen-Modell\n\n"
                        "**Ebene 1 — Basiswissen (alle Mitarbeitenden):**\n"
                        "Was ist KI? Welche Tools nutzen wir? Datenschutz. Kennzeichnung.\n\n"
                        "**Ebene 2 — Anwendungswissen (KI-Nutzer):**\n"
                        "Tool-Kompetenz, Stärken/Grenzen, Fehler erkennen, Qualitätssicherung.\n\n"
                        "**Ebene 3 — Steuerungswissen (Führungskräfte):**\n"
                        "EU AI Act, Risikobewertung, Governance, Verantwortungsstrukturen.\n\n"
                        "## Dokumentationspflicht\n\n"
                        "Kompetenzmaßnahmen müssen nachweisbar sein: Schulungsdaten, "
                        "Unterlagen, Kompetenznachweise. Jährliche Auffrischung empfohlen."
                    ),
                    "estimated_duration_minutes": 8,
                    "quiz": {
                        "title": "Quiz: Art. 4 KI-Kompetenz",
                        "passing_score": 66,
                        "questions": [
                            {
                                "text": "Wen betrifft Artikel 4 EU AI Act?",
                                "answers": [
                                    ("Nur Unternehmen, die KI-Systeme entwickeln und verkaufen", False),
                                    ("Nur Unternehmen mit mehr als 250 Mitarbeitenden", False),
                                    ("Alle Unternehmen, die KI-Systeme einsetzen — unabhängig von Größe und Branche", True),
                                    ("Nur Unternehmen, die Hochrisiko-KI einsetzen", False),
                                ],
                            },
                            {
                                "text": "Was beschreibt Ebene 2 (Anwendungswissen) im Drei-Ebenen-Modell?",
                                "answers": [
                                    ("Grundlegendes KI-Verständnis für alle Mitarbeitenden", False),
                                    ("Strategisches Wissen für Führungskräfte über EU AI Act", False),
                                    ("Tool-spezifische Kompetenz für Mitarbeitende, die KI regelmäßig einsetzen", True),
                                    ("Technisches Entwicklerwissen für IT-Spezialisten", False),
                                ],
                            },
                            {
                                "text": "Warum reicht ein einmaliges Schulungszertifikat nicht?",
                                "answers": [
                                    ("Weil Zertifikate grundsätzlich rechtlich unwirksam sind", False),
                                    ("Weil sich KI schnell weiterentwickelt und Kompetenz aktuell bleiben muss", True),
                                    ("Weil nur mündliche Prüfungen anerkannt werden", False),
                                    ("Weil jede Abteilung ein eigenes Zertifikat braucht", False),
                                ],
                            },
                        ],
                    },
                },
                {
                    "title": "3.3 — Von der Pflicht zum Plan: EU AI Act operationalisieren",
                    "content_text": (
                        "Die drei Kernpflichten für KMU und ein 90-Tage-Aktionsplan.\n\n"
                        "## Die drei Kernpflichten\n\n"
                        "1. **KI-Inventar:** Strukturierte Liste aller KI-Systeme mit "
                        "Risikoklasse, Datenbasis, Verantwortlichem.\n"
                        "2. **Risikobewertung:** Für Hochrisiko-KI: Risiken identifizieren, "
                        "bewerten, Maßnahmen definieren, dokumentieren.\n"
                        "3. **Kompetenznachweise:** Schulungen nach Drei-Ebenen-Modell, "
                        "dokumentiert und regelmäßig aktualisiert.\n\n"
                        "## Der 90-Tage-Plan\n\n"
                        "- **Monat 1:** Bestandsaufnahme (Shadow AI Radar, KI-Inventar)\n"
                        "- **Monat 2:** Klassifizierung und Risikobewertung\n"
                        "- **Monat 3:** Governance, Schulung, Verantwortlichkeiten\n\n"
                        "## Quick Win Woche 1\n\n"
                        "Fragen Sie in Ihrer nächsten Führungsrunde: 'Welche KI-Tools "
                        "setzt Ihr Team aktuell ein?' — 20 Minuten, sofort Erkenntnisse."
                    ),
                    "estimated_duration_minutes": 8,
                    "quiz": {
                        "title": "Quiz: EU AI Act Aktionsplan",
                        "passing_score": 66,
                        "questions": [
                            {
                                "text": "Welche drei Kernpflichten hat ein KMU nach EU AI Act als erste Priorität?",
                                "answers": [
                                    ("KI-Patent, Softwarelizenzen, IT-Infrastruktur", False),
                                    ("KI-Inventar erstellen, Risikobewertung, Kompetenznachweise sichern", True),
                                    ("Externe Prüfung, Datenbankregistrierung, Behördenantrag", False),
                                    ("KI-Strategie, Investitionsplan, Beratungsvertrag", False),
                                ],
                            },
                            {
                                "text": "Was ist der empfohlene Quick Win der ersten Woche?",
                                "answers": [
                                    ("Eine externe Anwaltskanzlei beauftragen", False),
                                    ("Alle KI-Tools sofort deinstallieren", False),
                                    ("In der Führungsrunde fragen: 'Welche KI-Tools setzt Ihr Team ein?'", True),
                                    ("Ein vollständiges KI-Governance-System implementieren", False),
                                ],
                            },
                            {
                                "text": "Was gehört in den Monat 2 des 90-Tage-Plans?",
                                "answers": [
                                    ("Shadow AI Radar und KI-Inventar erstellen", False),
                                    ("Klassifizierungs-Workshop und Risikobewertung der Hochrisiko-Systeme", True),
                                    ("KI-Nutzungsrichtlinie kommunizieren und Basisschulung durchführen", False),
                                    ("Externe Berater beauftragen und Budget planen", False),
                                ],
                            },
                        ],
                    },
                },
            ],
        },
    ],
}


class Command(BaseCommand):
    help = "Seed KI ohne Risiko™ learning modules (3 chapters, 9 lessons, 27 quiz questions)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing course before seeding",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            Course.objects.filter(
                title=COURSE_DATA["title"]
            ).delete()
            self.stdout.write("Deleted existing course.")

        # Category
        category, _ = Category.objects.get_or_create(
            name=COURSE_DATA["category"],
            defaults={"tenant_id": DEFAULT_TENANT},
        )
        self.stdout.write(f"Category: {category.name}")

        # Course
        course, created = Course.objects.get_or_create(
            title=COURSE_DATA["title"],
            defaults={
                "description": COURSE_DATA["description"],
                "status": COURSE_DATA["status"],
                "category": category,
                "tenant_id": DEFAULT_TENANT,
            },
        )
        action = "Created" if created else "Exists"
        self.stdout.write(f"{action} course: {course.title}")

        if not created and not options["reset"]:
            self.stdout.write(self.style.WARNING(
                "Course already exists. Use --reset to recreate."
            ))
            return

        # Chapters + Lessons + Quizzes
        total_lessons = 0
        total_questions = 0

        for ch_idx, ch_data in enumerate(COURSE_DATA["chapters"], 1):
            chapter = Chapter.objects.create(
                course=course,
                title=ch_data["title"],
                description=ch_data["description"],
                ordering=ch_idx,
                tenant_id=DEFAULT_TENANT,
            )
            self.stdout.write(f"  Chapter {ch_idx}: {chapter.title}")

            for ls_idx, ls_data in enumerate(ch_data["lessons"], 1):
                lesson = Lesson.objects.create(
                    chapter=chapter,
                    title=ls_data["title"],
                    content_type="text",
                    content_text=ls_data["content_text"],
                    estimated_duration_minutes=ls_data["estimated_duration_minutes"],
                    ordering=ls_idx,
                    is_mandatory=True,
                    tenant_id=DEFAULT_TENANT,
                )
                total_lessons += 1
                self.stdout.write(f"    Lesson {ls_idx}: {lesson.title}")

                # Quiz
                q_data = ls_data["quiz"]
                quiz = Quiz.objects.create(
                    chapter=chapter,
                    course=course,
                    title=q_data["title"],
                    passing_score=q_data["passing_score"],
                    max_attempts=0,
                    shuffle_questions=True,
                    is_active=True,
                    tenant_id=DEFAULT_TENANT,
                )

                for q_idx, question_data in enumerate(q_data["questions"], 1):
                    question = Question.objects.create(
                        quiz=quiz,
                        text=question_data["text"],
                        question_type="single_choice",
                        tenant_id=DEFAULT_TENANT,
                    )
                    total_questions += 1

                    for a_text, is_correct in question_data["answers"]:
                        Answer.objects.create(
                            question=question,
                            text=a_text,
                            is_correct=is_correct,
                            tenant_id=DEFAULT_TENANT,
                        )

                self.stdout.write(
                    f"      Quiz: {quiz.title} "
                    f"({len(q_data['questions'])} questions)"
                )

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Created: 1 course, "
            f"{len(COURSE_DATA['chapters'])} chapters, "
            f"{total_lessons} lessons, "
            f"{total_questions} questions"
        ))
