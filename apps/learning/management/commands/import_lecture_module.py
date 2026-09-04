"""Delivery-Projektion: writing-hub modul.json → learnfw Course/Chapter/Lesson.

Konsumiert das ``lecture-module/v1``-Bündel aus writing-hub (File-Pfad, kein
Live-RPC — KONZ-writing-hub-001 §5.1). Projektion:

    modul       → Course
    termin      → Chapter   („Termin n — <label>", seit writing-hub#994 K6: fünf
                  Termine, fünf Kapitel; darin je Einheit erst ein Einstieg mit
                  Umfang + Lernzielen, dann Themenblöcke, Übungen, Foliensatz)
    vorlesung   → Chapter   nur ohne ``termin`` (ältere Bündel): ordering =
                  dichtes 1..N nach position, lernziele → description
    themenblock → Lesson    (content_type="markdown")
    uebung      → Lesson    (content_type="markdown", „Übung: <titel>", nur die
                  Aufgabe — die Lösungsskizze schickt writing-hub nicht mit)
    deck_url    → Lesson    ans Kapitel-Ende, external_url=deck_url;
                  content_type="pdf" bei ``.pdf`` (writing-hub liefert das Deck
                  seit writing-hub#994 unter fester Adresse), sonst "pptx".
                  Fehlt/leer → kein Deck-Lesson.
    titelbild_url → Einstiegslektion, Bild (writing-hub#1010): erste Zeile der
                  Einstiegslektion einer Einheit, nur http(s), sonst ignoriert.

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
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

SCHEMA = "lecture-module/v1"


def _lernziele_text(lernziele: list) -> str:
    """Lernziele der Einheit → Kapitelbeschreibung (Markdown-Liste)."""
    ziele = [str(z).strip() for z in lernziele if str(z).strip()]
    if not ziele:
        return ""
    return "Lernziele:\n\n" + "\n".join(f"- {z}" for z in ziele)


def _titelbild_markdown(v: dict) -> str:
    """Titelbild-URL der Einheit als Markdown-Bildzeile (writing-hub#1010).

    Nur ``http://``/``https://`` — Schutz vor ``javascript:``/``data:`` in einem
    Feld, das aus einem fremden Bündel kommt. ``)`` und Leerzeichen werden
    prozent-kodiert, damit sie die Markdown-Bild-Syntax nicht vorzeitig
    schließen.
    """
    url = str(v.get("titelbild_url") or "").strip()
    if not url.lower().startswith(("http://", "https://")):
        return ""
    sichere_url = url.replace(")", "%29").replace(" ", "%20")
    return f"![Titelbild: {v.get('thema', '')}]({sichere_url})"


def _einstieg_text(v: dict) -> str:
    """Einstiegslektion einer Einheit in einem Termin-Kapitel.

    Titelbild (writing-hub#1010, sofern vorhanden) als erste Zeile, danach
    Umfang + Lernziele wie bisher.
    """
    teile = []
    titelbild = _titelbild_markdown(v)
    if titelbild:
        teile.append(titelbild)
    if v.get("umfang_ue"):
        teile.append(f"Umfang: {v['umfang_ue']} UE")
    lernziele = _lernziele_text(v.get("lernziele") or [])
    if lernziele:
        teile.append(lernziele)
    return "\n\n".join(teile)


@dataclass(frozen=True)
class Kapitel:
    titel: str
    beschreibung: str
    einheiten: list
    termin: bool  # True = Termin-Kapitel (mehrere Einheiten möglich), False = eine Einheit


def _kapitel(vorlesungen: list) -> list[Kapitel]:
    """Kapitelschnitt (writing-hub#994 K6).

    Trägt mindestens eine Einheit einen ``termin`` (Veranstaltungsblock aus
    writing-hub), wird **der Termin** zum Kapitel: fünf Termine, fünf Kapitel,
    darin die Einheiten in Reihenfolge, jede mit Einstieg, Themenblöcken,
    Übungen und Foliensatz. Ohne ``termin`` (ältere Bündel) bleibt es bei
    „eine Einheit = ein Kapitel" mit den Lernzielen als Kapitelbeschreibung.
    ``position`` darf in writing-hub Lücken/Dubletten haben → hier dicht 1..N.
    """
    vorlesungen = sorted(vorlesungen, key=lambda v: v.get("position", 0))
    if not any(v.get("termin") for v in vorlesungen):
        return [
            Kapitel(
                v.get("thema", f"Vorlesung {i}"),
                _lernziele_text(v.get("lernziele") or []),
                [v],
                False,
            )
            for i, v in enumerate(vorlesungen, 1)
        ]
    gruppen: dict[tuple, list] = {}
    for v in vorlesungen:
        t = v.get("termin") or {}
        # Einheiten ohne Termin landen hinten, sichtbar als eigenes Kapitel.
        schluessel = (t.get("position", 10**6), t.get("label") or "Ohne Termin")
        gruppen.setdefault(schluessel, []).append(v)
    kapitel = []
    for nr, ((_, label), einheiten) in enumerate(sorted(gruppen.items()), 1):
        beschreibung = "Einheiten:\n\n" + "\n".join(
            f"- {v.get('thema', '?')}" + (f" ({v['umfang_ue']} UE)" if v.get("umfang_ue") else "")
            for v in einheiten
        )
        kapitel.append(Kapitel(f"Termin {nr} — {label}", beschreibung, einheiten, True))
    return kapitel


def _lesson_text(block: dict, *, mit_notizen: bool = False) -> str:
    """Themenblock → Lektions-Text (Subtitle + Bullets als Markdown).

    Sprechernotizen sind für die Lehrperson geschrieben („die Teilnehmenden kommen
    aus Unternehmen, in denen …") — im Kurs für Teilnehmende bleiben sie draußen,
    wie die Lösungsskizze der Übungen (writing-hub#994 D3). ``--mit-notizen``
    nimmt sie ausdrücklich mit (kursiv).
    """
    parts: list[str] = []
    if block.get("subtitle"):
        parts.append(str(block["subtitle"]))
    bullets = block.get("bullets") or []
    if bullets:
        parts.append("\n".join(f"- {b}" for b in bullets))
    if mit_notizen and block.get("speaker_notes"):
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
        parser.add_argument(
            "--mit-notizen",
            action="store_true",
            help="Sprechernotizen der Themenblöcke mit in die Lektionen nehmen (Default: nur für die Lehrperson)",
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

        n_ch = n_ls = 0
        for ch_idx, kapitel in enumerate(_kapitel(data.get("vorlesungen", [])), 1):
            chapter = Chapter.objects.create(
                course=course,
                title=kapitel.titel,
                description=kapitel.beschreibung,
                ordering=ch_idx,
                tenant_id=tenant,
            )
            n_ch += 1
            ordering = 0
            for v in kapitel.einheiten:
                bloecke = v.get("themenbloecke") or []
                per_min = max(1, round(v.get("umfang_min", 0) / len(bloecke))) if bloecke else 1
                if kapitel.termin:
                    # Termin-Kapitel tragen mehrere Einheiten: jede beginnt mit ihrem
                    # Einstieg (Umfang + Lernziele), damit der Wechsel sichtbar ist.
                    ordering += 1
                    Lesson.objects.create(
                        chapter=chapter,
                        title=v.get("thema", f"Einheit {ordering}"),
                        content_type="markdown",
                        content_text=_einstieg_text(v),
                        estimated_duration_minutes=1,
                        ordering=ordering,
                        is_mandatory=True,
                        tenant_id=tenant,
                    )
                    n_ls += 1
                for block in bloecke:
                    ordering += 1
                    Lesson.objects.create(
                        chapter=chapter,
                        title=block.get("titel", f"Themenblock {ordering}"),
                        # "markdown" (gültiger learnfw-Choice); content_text IST Markdown.
                        # "text" ist NICHT in CONTENT_TYPE_CHOICES → kein Render-Handler.
                        content_type="markdown",
                        content_text=_lesson_text(block, mit_notizen=opts["mit_notizen"]),
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

                # Foliendeck ans Ende der Einheit: external_url, kein File-Upload. Seit
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
