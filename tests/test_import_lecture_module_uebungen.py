"""
import_lecture_module — Übungen, Lernziele, PDF-Deck, Veröffentlichen (writing-hub#994).

Das Bündel trägt seit writing-hub#994 ``lernziele``, ``uebungen`` (Titel + Aufgabe,
ohne Lösungsskizze) und in ``deck_url`` die feste Adresse des PDF auf writing-hub.
Belegt hier: Übungen werden Lektionen nach den Themenblöcken, Lernziele die
Kapitelbeschreibung, ein ``.pdf``-Deck wird eine PDF-Lektion, und ein Kurs geht
nur mit ``--veroeffentlichen`` live.

@pytest.mark.django_db: CI/PostgreSQL (ADR-179).
"""

import pytest
from django.core.management import call_command

from tests.test_import_lecture_module import MODUL, _bundle, _write


def _bundle_994():
    b = _bundle()
    v = b["vorlesungen"][1]  # V-eins, position 2 → Kapitel 1
    v["lernziele"] = [
        "Digitale Strategie von Digitalisierung unterscheiden",
        "Den Fall Kaeser einordnen",
    ]
    v["uebungen"] = [
        {
            "titel": "Einstiegs-Case",
            "aufgabe": "Ordnen Sie den Fall in die Womit-oder-Wie-Matrix ein.",
        },
        {"titel": "leer", "aufgabe": "   "},
    ]
    v["deck_url"] = "https://writing.example/vorlesungen/abc/deck.pdf"
    v["deck_datei"] = "folien/01-v-eins.pdf"
    return b


@pytest.mark.django_db
class TestImportUebungenUndDeck:
    def test_should_project_exercises_as_lessons_after_the_topic_blocks(self, tmp_path):
        from iil_learnfw.models import Chapter, Course, Lesson

        call_command("import_lecture_module", _write(tmp_path, _bundle_994()))
        chapter = Chapter.objects.get(course=Course.objects.get(title=MODUL), title="V-eins")
        lessons = list(Lesson.objects.filter(chapter=chapter).order_by("ordering"))
        assert [lek.title for lek in lessons] == [
            "TB-A",
            "Übung: Einstiegs-Case",
            "Foliensatz: V-eins",
        ]
        assert [lek.ordering for lek in lessons] == [1, 2, 3]
        uebung = lessons[1]
        assert uebung.content_type == "markdown"
        assert uebung.content_text == "Ordnen Sie den Fall in die Womit-oder-Wie-Matrix ein."
        assert "loesung" not in uebung.content_text.lower()

    def test_should_put_the_learning_goals_into_the_chapter_description(self, tmp_path):
        from iil_learnfw.models import Chapter, Course

        call_command("import_lecture_module", _write(tmp_path, _bundle_994()))
        course = Course.objects.get(title=MODUL)
        assert Chapter.objects.get(course=course, title="V-eins").description == (
            "Lernziele:\n\n- Digitale Strategie von Digitalisierung unterscheiden\n- Den Fall Kaeser einordnen"
        )
        # ohne Lernziele bleibt die Beschreibung leer (Positivkontrolle)
        assert Chapter.objects.get(course=course, title="V-zwei").description == ""

    def test_should_project_a_pdf_deck_url_to_a_pdf_lesson(self, tmp_path):
        from iil_learnfw.models import Chapter, Course, Lesson

        call_command("import_lecture_module", _write(tmp_path, _bundle_994()))
        chapter = Chapter.objects.get(course=Course.objects.get(title=MODUL), title="V-eins")
        deck = Lesson.objects.get(chapter=chapter, title="Foliensatz: V-eins")
        assert deck.content_type == "pdf"
        assert deck.external_url == "https://writing.example/vorlesungen/abc/deck.pdf"
        assert not deck.content_file  # keine Kopie: writing-hub ist die eine Quelle (D1)

    def test_should_keep_the_course_a_draft_unless_asked_to_publish(self, tmp_path):
        from iil_learnfw.models import Course

        path = _write(tmp_path, _bundle_994())
        call_command("import_lecture_module", path)
        assert Course.objects.get(title=MODUL).status == "draft"
        call_command("import_lecture_module", path, "--reset", "--veroeffentlichen")
        assert Course.objects.get(title=MODUL).status == "published"
