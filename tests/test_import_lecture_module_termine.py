"""
import_lecture_module — Termine als Kapitel (writing-hub#994 K6).

Trägt das Bündel je Einheit einen ``termin``, wird der Termin zum Kapitel und
die Einheiten darin laufen hintereinander, jede mit Einstieg (Umfang +
Lernziele), Themenblöcken, Übungen und Foliensatz. Ohne ``termin`` bleibt der
alte Schnitt (Positivkontrolle über die bestehenden Tests).

@pytest.mark.django_db: CI/PostgreSQL (ADR-179).
"""

import pytest
from django.core.management import call_command

from tests.test_import_lecture_module import MODUL, _bundle, _write

TERMIN_1 = {"label": "Di 15.09.2026 · 17:00–20:15 · Online", "position": 1, "format": "online"}
TERMIN_2 = {"label": "Fr 18.09.2026 · 15:00–20:00 · A.2.64", "position": 2, "format": "präsenz"}


def _bundle_termine():
    b = _bundle()
    v_eins, v_zwei = b["vorlesungen"][1], b["vorlesungen"][0]  # position 2 bzw. 5
    v_eins.update(
        termin=TERMIN_1,
        umfang_ue=3,
        lernziele=["Ziel A"],
        uebungen=[{"titel": "Einstieg", "aufgabe": "Aufgabe A."}],
        deck_url="https://writing.example/vorlesungen/eins/deck.pdf",
    )
    # dritte Einheit im selben Termin, dazwischen in der Position
    b["vorlesungen"].append(
        {
            "thema": "Übung: Werkzeugmappe",
            "position": 3,
            "umfang_min": 45,
            "sprache": "de",
            "niveau": "einführend",
            "termin": TERMIN_1,
            "umfang_ue": 1,
            "lernziele": [],
            "themenbloecke": [
                {"titel": "Mappe", "subtitle": None, "bullets": ["m"], "speaker_notes": None}
            ],
            "uebungen": [],
            "deck_url": "https://writing.example/vorlesungen/mappe/deck.pdf",
        }
    )
    v_zwei.update(termin=TERMIN_2, umfang_ue=4, lernziele=[])
    return b


@pytest.mark.django_db
class TestTermineAlsKapitel:
    def test_should_make_one_chapter_per_termin_with_units_in_sequence(self, tmp_path):
        from iil_learnfw.models import Chapter, Course, Lesson

        call_command("import_lecture_module", _write(tmp_path, _bundle_termine()))
        course = Course.objects.get(title=MODUL)
        kapitel = list(Chapter.objects.filter(course=course).order_by("ordering"))
        assert [k.title for k in kapitel] == [
            f"Termin 1 — {TERMIN_1['label']}",
            f"Termin 2 — {TERMIN_2['label']}",
        ]
        assert (
            kapitel[0].description == "Einheiten:\n- V-eins (3 UE)\n- Übung: Werkzeugmappe (1 UE)"
        )
        titel = [
            lek.title for lek in Lesson.objects.filter(chapter=kapitel[0]).order_by("ordering")
        ]
        assert titel == [
            "V-eins",
            "TB-A",
            "Übung: Einstieg",
            "Foliensatz: V-eins",
            "Übung: Werkzeugmappe",
            "Mappe",
            "Foliensatz: Übung: Werkzeugmappe",
        ]
        einstieg = Lesson.objects.get(chapter=kapitel[0], title="V-eins")
        assert einstieg.content_text == "Umfang: 3 UE\n\nLernziele:\n- Ziel A"

    def test_should_keep_lernziele_in_the_chapter_when_no_termin_is_given(self, tmp_path):
        """Positivkontrolle: ohne termin bleibt „eine Einheit = ein Kapitel", kein Einstieg."""
        from iil_learnfw.models import Chapter, Course, Lesson

        b = _bundle()
        b["vorlesungen"][1]["lernziele"] = ["Ziel A"]
        call_command("import_lecture_module", _write(tmp_path, b))
        course = Course.objects.get(title=MODUL)
        kapitel = Chapter.objects.get(course=course, title="V-eins")
        assert kapitel.description == "Lernziele:\n- Ziel A"
        assert [
            lek.title for lek in Lesson.objects.filter(chapter=kapitel).order_by("ordering")
        ] == ["TB-A"]
