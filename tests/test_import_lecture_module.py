"""
import_lecture_module — Delivery-Projektion writing-hub → learnfw.

Konsumiert ein lecture-module/v1-Bündel und legt Course/Chapter/Lesson an.
Läuft über den Default-Tenant (kein --tenant), um Tenant-Scoping der
learnfw-Manager nicht zu treffen.

@pytest.mark.django_db: CI/PostgreSQL (ADR-179).
"""

import json

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

MODUL = "Test-Modul-Import"


def _bundle(**over):
    b = {
        "schema": "lecture-module/v1",
        "modul": {"titel": MODUL, "beschreibung": "desc"},
        "vorlesungen": [
            {
                "thema": "V-zwei",
                "position": 5,
                "umfang_min": 90,
                "sprache": "de",
                "niveau": "einführend",
                "themenbloecke": [
                    {"titel": "TB1", "subtitle": "s", "bullets": ["a", "b"], "speaker_notes": "n"}
                ],
            },
            {
                "thema": "V-eins",
                "position": 2,
                "umfang_min": 60,
                "sprache": "de",
                "niveau": "einführend",
                "themenbloecke": [
                    {"titel": "TB-A", "subtitle": None, "bullets": ["x"], "speaker_notes": None}
                ],
            },
        ],
        "skipped_in_arbeit": 0,
    }
    b.update(over)
    return b


def _write(tmp_path, bundle):
    p = tmp_path / "modul.json"
    p.write_text(json.dumps(bundle), encoding="utf-8")
    return str(p)


@pytest.mark.django_db
class TestImportLectureModule:
    def test_should_project_modul_to_course_chapters_lessons(self, tmp_path):
        from iil_learnfw.models import Chapter, Course, Lesson

        call_command("import_lecture_module", _write(tmp_path, _bundle()))
        course = Course.objects.get(title=MODUL)
        chapters = list(Chapter.objects.filter(course=course).order_by("ordering"))
        # nach position (2 vor 5) sortiert, ordering dicht 1..N normalisiert
        assert [c.title for c in chapters] == ["V-eins", "V-zwei"]
        assert [c.ordering for c in chapters] == [1, 2]
        lessons = Lesson.objects.filter(chapter=chapters[0])
        assert lessons.count() == 1
        ls = lessons.first()
        # gültiger learnfw-Choice (nicht das frühere out-of-enum "text")
        valid = {c[0] for c in ls._meta.get_field("content_type").choices}
        assert ls.content_type == "markdown"
        assert ls.content_type in valid
        assert "- x" in ls.content_text

    def test_should_reject_wrong_schema(self, tmp_path):
        with pytest.raises(CommandError):
            call_command("import_lecture_module", _write(tmp_path, _bundle(schema="other/v9")))

    def test_should_guard_against_double_import(self, tmp_path):
        path = _write(tmp_path, _bundle())
        call_command("import_lecture_module", path)
        with pytest.raises(CommandError):
            call_command("import_lecture_module", path)

    def test_should_recreate_on_reset_without_duplicating(self, tmp_path):
        from iil_learnfw.models import Chapter, Course

        path = _write(tmp_path, _bundle())
        call_command("import_lecture_module", path)
        call_command("import_lecture_module", path, "--reset")
        course = Course.objects.get(title=MODUL)
        assert Chapter.objects.filter(course=course).count() == 2

    def test_should_error_on_missing_file(self):
        with pytest.raises(CommandError):
            call_command("import_lecture_module", "/nonexistent/modul.json")

    def test_should_project_deck_url_to_pptx_lesson(self, tmp_path):
        from iil_learnfw.models import Chapter, Course, Lesson

        bundle = _bundle()
        bundle["vorlesungen"][0]["deck_url"] = "https://decks.example/v-zwei.pptx"
        call_command("import_lecture_module", _write(tmp_path, bundle))
        course = Course.objects.get(title=MODUL)
        # V-zwei (position 5) → ordering 2; trägt das Deck
        chapter = Chapter.objects.get(course=course, title="V-zwei")
        deck = Lesson.objects.get(chapter=chapter, content_type="pptx")
        assert deck.external_url == "https://decks.example/v-zwei.pptx"
        assert deck.ordering == len(bundle["vorlesungen"][0]["themenbloecke"]) + 1
        # andere Vorlesung ohne deck_url → kein pptx-Lesson
        other = Chapter.objects.get(course=course, title="V-eins")
        assert not Lesson.objects.filter(chapter=other, content_type="pptx").exists()

    def test_should_skip_empty_deck_url(self, tmp_path):
        from iil_learnfw.models import Course, Lesson

        bundle = _bundle()
        bundle["vorlesungen"][0]["deck_url"] = "  "  # leer/whitespace → kein Deck
        call_command("import_lecture_module", _write(tmp_path, bundle))
        course = Course.objects.get(title=MODUL)
        assert not Lesson.objects.filter(chapter__course=course, content_type="pptx").exists()
