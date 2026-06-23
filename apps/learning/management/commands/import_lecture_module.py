"""Delivery-Projektion: writing-hub modul.json → learnfw Course/Chapter/Lesson.

Konsumiert das ``lecture-module/v1``-Bündel aus writing-hub (File-Pfad, kein
Live-RPC — KONZ-writing-hub-001 §5.1). Projektion:

    modul       → Course
    vorlesung   → Chapter   (ordering = dichtes 1..N nach position)
    themenblock → Lesson    (content_type="text")
    deck_url    → Lesson    (content_type="pptx", external_url=deck_url) ans
                  Kapitel-Ende — optional; das Deck wird extern (pptx-hub)
                  gerendert/gehostet, deck_url wird im Bündel manuell gefüllt
                  (File-Pfad-v0). Fehlt/leer → kein Deck-Lesson.

Idempotenz wie ``seed_lernmodule``: Course per (title, tenant) angelegt;
ohne ``--reset`` bricht ein zweiter Lauf ab (kein stilles Verdoppeln).
``unique_together(course, ordering)`` erzwingt die Normalisierung auf 1..N.

Usage:
    python manage.py import_lecture_module modul.json --tenant <uuid> [--reset]
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

SCHEMA = "lecture-module/v1"


def _lesson_text(block: dict) -> str:
    """Themenblock → Lektions-Text (Subtitle + Bullets als Markdown + Notiz)."""
    parts: list[str] = []
    if block.get("subtitle"):
        parts.append(str(block["subtitle"]))
    bullets = block.get("bullets") or []
    if bullets:
        parts.append("\n".join(f"- {b}" for b in bullets))
    if block.get("speaker_notes"):
        parts.append(f"_{block['speaker_notes']}_")
    return "\n\n".join(parts)


class Command(BaseCommand):
    help = "Projiziert ein writing-hub modul.json (lecture-module/v1) in learnfw."

    def add_arguments(self, parser):
        parser.add_argument("bundle", help="Pfad zur modul.json (lecture-module/v1)")
        parser.add_argument(
            "--tenant",
            help="Tenant-UUID (Default: IIL_LEARNFW['DEFAULT_TENANT_ID'])",
        )
        parser.add_argument("--category", default="Vorlesungen", help="learnfw-Category-Name")
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Vorhandenen Kurs (gleicher Titel + Tenant) vorher löschen",
        )

    def handle(self, *args, **opts):
        from iil_learnfw.models import Category, Chapter, Course, Lesson

        path = Path(opts["bundle"])
        if not path.exists():
            raise CommandError(f"Datei nicht gefunden: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise CommandError(f"Kein gültiges JSON: {e}") from e

        if data.get("schema") != SCHEMA:
            raise CommandError(f"Erwarte schema={SCHEMA!r}, gefunden {data.get('schema')!r}")

        tenant_raw = opts.get("tenant") or settings.IIL_LEARNFW.get("DEFAULT_TENANT_ID")
        try:
            tenant = uuid.UUID(str(tenant_raw))
        except (TypeError, ValueError) as e:
            raise CommandError(f"Ungültige Tenant-UUID: {tenant_raw!r}") from e

        modul = data.get("modul") or {}
        title = modul.get("titel")
        if not title:
            raise CommandError("Bündel ohne modul.titel — nichts zu importieren.")

        if opts["reset"]:
            deleted, _ = Course.objects.filter(title=title, tenant_id=tenant).delete()
            self.stdout.write(f"Reset: {deleted} Objekte gelöscht.")

        category, _ = Category.objects.get_or_create(
            name=opts["category"], defaults={"tenant_id": tenant}
        )

        course, created = Course.objects.get_or_create(
            title=title,
            tenant_id=tenant,
            defaults={
                "description": modul.get("beschreibung", ""),
                "status": "draft",  # importierte Inhalte nicht auto-publishen
                "category": category,
            },
        )
        if not created and not opts["reset"]:
            raise CommandError(
                f"Kurs {title!r} (Tenant {tenant}) existiert bereits — --reset zum Neuanlegen."
            )

        # position darf in writing-hub Lücken/Dubletten haben → hier dicht 1..N.
        vorlesungen = sorted(data.get("vorlesungen", []), key=lambda v: v.get("position", 0))
        n_ch = n_ls = 0
        for ch_idx, v in enumerate(vorlesungen, 1):
            chapter = Chapter.objects.create(
                course=course,
                title=v.get("thema", f"Vorlesung {ch_idx}"),
                description="",
                ordering=ch_idx,
                tenant_id=tenant,
            )
            n_ch += 1
            bloecke = v.get("themenbloecke") or []
            per_min = max(1, round(v.get("umfang_min", 0) / len(bloecke))) if bloecke else 1
            for ls_idx, block in enumerate(bloecke, 1):
                Lesson.objects.create(
                    chapter=chapter,
                    title=block.get("titel", f"Themenblock {ls_idx}"),
                    content_type="text",
                    content_text=_lesson_text(block),
                    estimated_duration_minutes=per_min,
                    ordering=ls_idx,
                    is_mandatory=True,
                    tenant_id=tenant,
                )
                n_ls += 1

            # Foliendeck (pptx-hub-Render, extern via deck_url) → eigene
            # Lesson(content_type=pptx) ans Kapitel-Ende. external_url, kein
            # File-Upload (File-Pfad). Leer/fehlend → kein Deck-Lesson.
            deck_url = (v.get("deck_url") or "").strip()
            if deck_url:
                Lesson.objects.create(
                    chapter=chapter,
                    title=f"Foliendeck: {v.get('thema', '')}".rstrip(": ") or "Foliendeck",
                    content_type="pptx",
                    external_url=deck_url,
                    estimated_duration_minutes=max(1, v.get("umfang_min", 0) or 5),
                    ordering=len(bloecke) + 1,
                    is_mandatory=True,
                    tenant_id=tenant,
                )
                n_ls += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Importiert: Kurs {title!r} — {n_ch} Kapitel, {n_ls} Lektionen (Tenant {tenant})."
            )
        )
