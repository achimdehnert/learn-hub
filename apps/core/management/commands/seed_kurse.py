"""Seed: KI-ohne-Risiko-Kurs mit 9 Kapiteln und 27 Lektionen.

Usage:
    python manage.py seed_kurse
    python manage.py seed_kurse --reset
"""

from django.core.management.base import BaseCommand

from apps.core.management.commands._kurs_data import CHAPTERS, COURSE


class Command(BaseCommand):
    help = "Seed den vollständigen KI-ohne-Risiko-Kurs"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Kurs löschen und neu anlegen")

    def handle(self, *args, **options):
        from iil_learnfw.models.course import Category, Chapter, Course, Lesson

        if options["reset"]:
            Course.objects.filter(slug=COURSE["slug"]).delete()
            self.stdout.write("Vorhandenen Kurs gelöscht.")

        cat, _ = Category.objects.get_or_create(
            slug="ki-governance", defaults={"name": COURSE["category_name"]},
        )

        course, created = Course.objects.update_or_create(
            slug=COURSE["slug"],
            defaults={
                "title": COURSE["title"],
                "description": COURSE["description"],
                "category": cat,
                "estimated_duration_minutes": COURSE["estimated_duration_minutes"],
                "status": "published",
            },
        )
        action = "erstellt" if created else "aktualisiert"
        self.stdout.write(f"Kurs {action}: {course.title}")

        for ch_data in CHAPTERS:
            chapter, _ = Chapter.objects.update_or_create(
                course=course,
                ordering=ch_data["ordering"],
                defaults={
                    "title": ch_data["title"],
                    "description": ch_data["description"],
                },
            )
            self.stdout.write(f"  Kapitel {ch_data['ordering']}: {chapter.title}")

            for ls_data in ch_data["lessons"]:
                lesson, _ = Lesson.objects.update_or_create(
                    chapter=chapter,
                    ordering=ls_data["ordering"],
                    defaults={
                        "title": ls_data["title"],
                        "content_type": "markdown",
                        "content_text": ls_data["content"],
                        "estimated_duration_minutes": ls_data["duration"],
                    },
                )
                self.stdout.write(f"    Lektion {ls_data['ordering']}: {lesson.title}")

        total_lessons = sum(len(ch["lessons"]) for ch in CHAPTERS)
        self.stdout.write(self.style.SUCCESS(
            f"\nFertig: {len(CHAPTERS)} Kapitel, {total_lessons} Lektionen."
        ))
