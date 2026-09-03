"""Delivery-Projektion: writing-hub modul.json → learnfw Course/Chapter/Lesson.

Konsumiert das ``lecture-module/v1``-Bündel aus writing-hub (File-Pfad, kein
Live-RPC — KONZ-writing-hub-001 §5.1). Projektion:

    modul       → Course
    vorlesung   → Chapter   (ordering = dichtes 1..N nach position;
                  lernziele → description)
    themenblock → Lesson    (content_type="markdown")
    uebung      → Lesson    (content_type="markdown", „Übung: <titel>", nur die
                  Aufgabe — die Lösungsskizze schickt writing-hub nicht mit)
    deck_url    → Lesson    ans Kapitel-Ende, external_url=deck_url;
                  content_type="pdf" bei ``.pdf`` (writing-hub liefert das Deck
                  seit writing-hub#994 unter fester Adresse), sonst "pptx".
                  Fehlt/leer → kein Deck-Lesson.

Idempotenz wie ``seed_lernmodule``: Course per (title, tenant) angelegt;
ohne ``--reset`` bricht ein zweiter Lauf ab (kein stilles Verdoppeln).
``unique_together(course, ordering)`` erzwingt die Normalisierung auf 1..N.
Importierte Kurse bleiben ``draft``; ``--veroeffentlichen`` setzt sie in
demselben Lauf live — ausdrücklich, nie als Nebenwirkung.

Usage:
    python manage.py import_lecture_module modul.json --tenant <uuid> [--reset] [--veroeffentlichen]
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

SCHEMA = "lecture-module/v1"


def _lernziele_text(lernziele: list) -> str:
    """Lernziele der Einheit → Kapitelbeschreibung (Markdown-Liste)."""
    ziele = [str(z).strip() for z in lernziele if str(z).strip()]
    if not ziele:
        return ""
    return "Lernziele:\n" + "\n".join(f"- {z}" for z in ziele)


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
        parser.add_argument(
            "--veroeffentlichen",
            action="store_true",
            help="Kurs nach dem Import auf 'published' setzen (Default: bleibt Entwurf)",
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
        if opts["veroeffentlichen"] and course.status != "published":
            course.status = "published"
            course.save(update_fields=["status"])

        # position darf in writing-hub Lücken/Dubletten haben → hier dicht 1..N.
        vorlesungen = sorted(data.get("vorlesungen", []), key=lambda v: v.get("position", 0))
        n_ch = n_ls = 0
        for ch_idx, v in enumerate(vorlesungen, 1):
            chapter = Chapter.objects.create(
                course=course,
                title=v.get("thema", f"Vorlesung {ch_idx}"),
                description=_lernziele_text(v.get("lernziele") or []),
                ordering=ch_idx,
                tenant_id=tenant,
            )
            n_ch += 1
            bloecke = v.get("themenbloecke") or []
            per_min = max(1, round(v.get("umfang_min", 0) / len(bloecke))) if bloecke else 1
            ordering = 0
            for block in bloecke:
                ordering += 1
                Lesson.objects.create(
                    chapter=chapter,
                    title=block.get("titel", f"Themenblock {ordering}"),
                    # "markdown" (gültiger learnfw-Choice); content_text IST Markdown.
                    # "text" ist NICHT in CONTENT_TYPE_CHOICES → kein Render-Handler.
                    content_type="markdown",
                    content_text=_lesson_text(block),
                    estimated_duration_minutes=per_min,
                    ordering=ordering,
                    is_mandatory=True,
                    tenant_id=tenant,
                )
                n_ls += 1

            # Übungen (writing-hub#994 K2): je eine Lektion mit der Aufgabe, nach
            # den Themenblöcken. Die Lösungsskizze ist im Bündel nicht enthalten.
            for ueb in v.get("uebungen") or []:
                aufgabe = (ueb.get("aufgabe") or "").strip()
                if not aufgabe:
                    continue
                ordering += 1
                Lesson.objects.create(
                    chapter=chapter,
                    title=f"Übung: {ueb.get('titel') or ordering}",
                    content_type="markdown",
                    content_text=aufgabe,
                    estimated_duration_minutes=per_min,
                    ordering=ordering,
                    is_mandatory=True,
                    tenant_id=tenant,
                )
                n_ls += 1

            # Foliendeck ans Kapitel-Ende: external_url, kein File-Upload. Seit
            # writing-hub#994 ist deck_url die feste Adresse des PDF auf writing-hub
            # (…/deck.pdf) → content_type "pdf"; ein .pptx bleibt "pptx".
            # Leer/fehlend → kein Deck-Lesson.
            deck_url = (v.get("deck_url") or "").strip()
            if deck_url:
                ordering += 1
                Lesson.objects.create(
                    chapter=chapter,
                    title=f"Foliensatz: {v.get('thema', '')}".rstrip(": ") or "Foliensatz",
                    content_type="pdf" if deck_url.lower().endswith(".pdf") else "pptx",
                    external_url=deck_url,
                    estimated_duration_minutes=max(1, v.get("umfang_min", 0) or 5),
                    ordering=ordering,
                    is_mandatory=True,
                    tenant_id=tenant,
                )
                n_ls += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Importiert: Kurs {title!r} — {n_ch} Kapitel, {n_ls} Lektionen (Tenant {tenant})."
            )
        )
