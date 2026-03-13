"""Seed-Daten: KI ohne Risiko — 9 Kapitel, 27 Lektionen."""
from apps.core.management.commands._kurs_kap1_5 import CHAPTERS_1_5
from apps.core.management.commands._kurs_kap6_9 import CHAPTERS_6_9

COURSE = {
    "title": "KI ohne Risiko\u2122 \u2014 Grundlagen der KI-Souver\u00e4nit\u00e4t",
    "slug": "ki-ohne-risikotm-grundlagen-der-ki-souveranitat",
    "description": (
        "Der Grundlagenkurs f\u00fcr Gesch\u00e4ftsf\u00fchrer und F\u00fchrungskr\u00e4fte im Mittelstand. "
        "In 9 kompakten Modulen lernen Sie, wie Sie KI souver\u00e4n, kontrolliert und "
        "rechtskonform einsetzen \u2014 von Shadow AI \u00fcber kognitive Fallen bis zum EU AI Act."
    ),
    "category_name": "KI-Governance",
    "estimated_duration_minutes": 180,
}

CHAPTERS = CHAPTERS_1_5 + CHAPTERS_6_9
