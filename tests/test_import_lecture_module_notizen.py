"""
import_lecture_module — Sprechernotizen bleiben draußen (writing-hub#994, D3-Analogie).

Die Notizen eines Themenblocks sind für die Lehrperson geschrieben. Im Kurs für
Teilnehmende erscheinen sie nur mit ``--mit-notizen``; sonst tragen die Lektionen
Untertitel und Bullets.

@pytest.mark.django_db: CI/PostgreSQL (ADR-179).
"""

import pytest
from django.core.management import call_command

from tests.test_import_lecture_module import MODUL, _bundle, _write


def _lektion_tb1():
    from iil_learnfw.models import Course, Lesson

    return Lesson.objects.get(chapter__course=Course.objects.get(title=MODUL), title="TB1")


@pytest.mark.django_db
class TestSprechernotizen:
    def test_should_leave_speaker_notes_out_by_default(self, tmp_path):
        call_command("import_lecture_module", _write(tmp_path, _bundle()))
        text = _lektion_tb1().content_text
        assert text == "s\n\n- a\n- b"
        assert "_n_" not in text

    def test_should_include_speaker_notes_only_when_asked(self, tmp_path):
        call_command("import_lecture_module", _write(tmp_path, _bundle()), "--mit-notizen")
        assert _lektion_tb1().content_text == "s\n\n- a\n- b\n\n_n_"
