"""ADR-142: Assessment Engine models.

7 new models: AssessmentType, AssessmentDimension, AssessmentQuestion,
AssessmentMaturityLevel, AssessmentRecommendation, AssessmentAttempt, AssessmentReport.
"""

import uuid

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("iil_learnfw", "0001_initial"),
    ]

    operations = [
        # ------------------------------------------------------------------
        # AssessmentType
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="AssessmentType",
            fields=[
                ("tenant_id", models.UUIDField(blank=True, db_index=True, help_text="Tenant UUID (NULL = single-tenant mode or global content).", null=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("public_id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name="Public ID")),
                ("key", models.CharField(max_length=50, unique=True, verbose_name="Schlüssel")),
                ("title", models.CharField(max_length=300, verbose_name="Titel")),
                ("slug", models.SlugField(max_length=300, unique=True, verbose_name="Slug")),
                ("description", models.TextField(blank=True, verbose_name="Beschreibung")),
                ("scoring_strategy", models.CharField(choices=[("likert", "Likert-Skala (1-N)"), ("weighted_likert", "Gewichtete Likert-Skala"), ("quiz", "Quiz (Richtig/Falsch)"), ("survey", "Umfrage (kein Scoring)")], default="likert", max_length=30, verbose_name="Scoring-Strategie")),
                ("scale_min", models.PositiveSmallIntegerField(default=1, verbose_name="Skalenminimum")),
                ("scale_max", models.PositiveSmallIntegerField(default=4, verbose_name="Skalenmaximum")),
                ("scale_labels", models.JSONField(default=list, help_text='Schema: [{"value": 1, "label": "Trifft nicht zu"}, ...]', verbose_name="Skalen-Labels")),
                ("is_public", models.BooleanField(default=False, verbose_name="Öffentlich (anonym ohne Login)")),
                ("is_active", models.BooleanField(default=True, verbose_name="Aktiv")),
                ("passing_score", models.PositiveSmallIntegerField(default=0, help_text="0 = kein Bestehen erforderlich. Wert in Prozent (0-100).", verbose_name="Mindest-Prozentsatz zum Bestehen")),
                ("certificate_enabled", models.BooleanField(default=False, verbose_name="Zertifikat aktiviert")),
                ("report_enabled", models.BooleanField(default=True, verbose_name="Bericht aktiviert")),
                ("reassessment_months", models.PositiveSmallIntegerField(default=6, verbose_name="Re-Assessment nach N Monaten")),
                ("retention_days", models.PositiveIntegerField(default=730, help_text="DSGVO: Standard 730 Tage (24 Monate).", verbose_name="Aufbewahrungsfrist (Tage)")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="Gelöscht am")),
                ("course", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assessments", to="iil_learnfw.course", verbose_name="Verknüpfter Kurs")),
            ],
            options={
                "verbose_name": "Assessment-Typ",
                "verbose_name_plural": "Assessment-Typen",
                "ordering": ["title"],
            },
        ),
        migrations.AddConstraint(
            model_name="assessmenttype",
            constraint=models.CheckConstraint(
                check=models.Q(scale_min__lt=models.F("scale_max")),
                name="assessment_type_scale_min_lt_max",
            ),
        ),
        migrations.AddConstraint(
            model_name="assessmenttype",
            constraint=models.CheckConstraint(
                check=models.Q(passing_score__lte=100),
                name="assessment_type_passing_score_max_100",
            ),
        ),
        # ------------------------------------------------------------------
        # AssessmentDimension
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="AssessmentDimension",
            fields=[
                ("tenant_id", models.UUIDField(blank=True, db_index=True, help_text="Tenant UUID (NULL = single-tenant mode or global content).", null=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("public_id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name="Public ID")),
                ("key", models.CharField(max_length=50, verbose_name="Schlüssel")),
                ("label", models.CharField(max_length=200, verbose_name="Bezeichnung")),
                ("weight", models.DecimalField(decimal_places=2, default=1.0, help_text="Wird von WeightedLikertScoring verwendet. Standard: 1.0", max_digits=4, verbose_name="Gewichtung")),
                ("sort_order", models.PositiveSmallIntegerField(default=0, verbose_name="Sortierreihenfolge")),
                ("is_active", models.BooleanField(default=True, verbose_name="Aktiv")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="Gelöscht am")),
                ("assessment_type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dimensions", to="iil_learnfw.assessmenttype", verbose_name="Assessment-Typ")),
            ],
            options={
                "verbose_name": "Assessment-Dimension",
                "verbose_name_plural": "Assessment-Dimensionen",
                "ordering": ["sort_order"],
            },
        ),
        migrations.AddConstraint(
            model_name="assessmentdimension",
            constraint=models.UniqueConstraint(
                condition=models.Q(deleted_at__isnull=True),
                fields=["assessment_type", "key"],
                name="uq_assessment_dimension_type_key_active",
            ),
        ),
        # ------------------------------------------------------------------
        # AssessmentQuestion
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="AssessmentQuestion",
            fields=[
                ("tenant_id", models.UUIDField(blank=True, db_index=True, help_text="Tenant UUID (NULL = single-tenant mode or global content).", null=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("public_id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name="Public ID")),
                ("key", models.CharField(blank=True, help_text="Idempotenter Seed-Key (z.B. 'strat_gov_q1'). Leer = text-basierte Deduplizierung.", max_length=100, verbose_name="Stabiler Schlüssel")),
                ("text", models.TextField(verbose_name="Fragetext")),
                ("help_text", models.TextField(blank=True, verbose_name="Hilfetext")),
                ("sort_order", models.PositiveSmallIntegerField(default=0, verbose_name="Sortierreihenfolge")),
                ("is_active", models.BooleanField(default=True, verbose_name="Aktiv")),
                ("version", models.PositiveSmallIntegerField(default=1, help_text="Wird bei Textänderungen inkrementiert. Historische Antworten bleiben zuordenbar.", verbose_name="Version")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="Gelöscht am")),
                ("dimension", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="iil_learnfw.assessmentdimension", verbose_name="Dimension")),
            ],
            options={
                "verbose_name": "Assessment-Frage",
                "verbose_name_plural": "Assessment-Fragen",
                "ordering": ["dimension__sort_order", "sort_order"],
            },
        ),
        # ------------------------------------------------------------------
        # AssessmentMaturityLevel
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="AssessmentMaturityLevel",
            fields=[
                ("tenant_id", models.UUIDField(blank=True, db_index=True, help_text="Tenant UUID (NULL = single-tenant mode or global content).", null=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("public_id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name="Public ID")),
                ("key", models.CharField(max_length=50, verbose_name="Schlüssel")),
                ("label", models.CharField(max_length=200, verbose_name="Bezeichnung")),
                ("description", models.TextField(verbose_name="Beschreibung")),
                ("color", models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(message="Muss ein gültiger Hex-Farbcode sein (z. B. #1A2B3C).", regex="^#[0-9A-Fa-f]{6}$")], verbose_name="Farbe (Hex)")),
                ("icon", models.CharField(blank=True, max_length=50, verbose_name="Icon")),
                ("pct_min", models.PositiveSmallIntegerField(verbose_name="Mindest-Prozent")),
                ("pct_max", models.PositiveSmallIntegerField(verbose_name="Maximal-Prozent")),
                ("sort_order", models.PositiveSmallIntegerField(default=0, verbose_name="Sortierreihenfolge")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="Gelöscht am")),
                ("assessment_type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="maturity_levels", to="iil_learnfw.assessmenttype", verbose_name="Assessment-Typ")),
            ],
            options={
                "verbose_name": "Assessment-Reifegrad",
                "verbose_name_plural": "Assessment-Reifegrade",
                "ordering": ["pct_min"],
            },
        ),
        migrations.AddConstraint(
            model_name="assessmentmaturitylevel",
            constraint=models.CheckConstraint(
                check=models.Q(pct_min__lte=models.F("pct_max")),
                name="assessment_maturity_pct_min_lte_max",
            ),
        ),
        migrations.AddConstraint(
            model_name="assessmentmaturitylevel",
            constraint=models.CheckConstraint(
                check=models.Q(pct_max__lte=100),
                name="assessment_maturity_pct_max_lte_100",
            ),
        ),
        migrations.AddConstraint(
            model_name="assessmentmaturitylevel",
            constraint=models.UniqueConstraint(
                condition=models.Q(deleted_at__isnull=True),
                fields=["assessment_type", "key"],
                name="uq_assessment_maturity_type_key_active",
            ),
        ),
        # ------------------------------------------------------------------
        # AssessmentRecommendation
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="AssessmentRecommendation",
            fields=[
                ("tenant_id", models.UUIDField(blank=True, db_index=True, help_text="Tenant UUID (NULL = single-tenant mode or global content).", null=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("public_id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name="Public ID")),
                ("threshold_below_pct", models.PositiveSmallIntegerField(help_text="Empfehlung aktiv wenn Dimensions-Score (%) unter diesem Wert liegt. 0-100.", verbose_name="Schwellenwert (%)")),
                ("title", models.CharField(max_length=300, verbose_name="Titel")),
                ("description", models.TextField(verbose_name="Beschreibung")),
                ("priority", models.PositiveSmallIntegerField(default=0, verbose_name="Priorität")),
                ("external_url", models.URLField(blank=True, verbose_name="Externe URL")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="Gelöscht am")),
                ("dimension", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="recommendations", to="iil_learnfw.assessmentdimension", verbose_name="Dimension")),
                ("course", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="recommended_by", to="iil_learnfw.course", verbose_name="Empfohlener Kurs")),
                ("lesson", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="recommended_by", to="iil_learnfw.lesson", verbose_name="Empfohlene Lektion")),
            ],
            options={
                "verbose_name": "Assessment-Empfehlung",
                "verbose_name_plural": "Assessment-Empfehlungen",
                "ordering": ["priority"],
            },
        ),
        migrations.AddConstraint(
            model_name="assessmentrecommendation",
            constraint=models.CheckConstraint(
                check=models.Q(threshold_below_pct__lte=100),
                name="assessment_rec_threshold_lte_100",
            ),
        ),
        # ------------------------------------------------------------------
        # AssessmentAttempt
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="AssessmentAttempt",
            fields=[
                ("tenant_id", models.UUIDField(blank=True, db_index=True, help_text="Tenant UUID (NULL = single-tenant mode or global content).", null=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("public_id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name="Public ID")),
                ("answers", models.JSONField(default=dict, help_text='Schema: {str(question.public_id): {"question_text": "...", "value": 3, "question_version": 1}}', verbose_name="Antworten (Snapshot)")),
                ("scores", models.JSONField(default=dict, help_text='Schema: {dimension_key: {"score": "2.75", "pct": 58, "weight": "1.00"}}', verbose_name="Dimensions-Scores")),
                ("total_score", models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name="Gesamt-Rohscore")),
                ("total_pct", models.PositiveSmallIntegerField(default=0, verbose_name="Gesamt-Prozent (0-100)")),
                ("weakest_dimension", models.CharField(blank=True, max_length=50, verbose_name="Schwächste Dimension")),
                ("strongest_dimension", models.CharField(blank=True, max_length=50, verbose_name="Stärkste Dimension")),
                ("started_at", models.DateTimeField(auto_now_add=True, verbose_name="Gestartet am")),
                ("completed_at", models.DateTimeField(blank=True, null=True, verbose_name="Abgeschlossen am")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")),
                ("ip_hash", models.CharField(blank=True, max_length=64, verbose_name="IP-Hash")),
                ("retention_expires_at", models.DateTimeField(blank=True, null=True, verbose_name="Aufbewahrung endet am")),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="Gelöscht am")),
                ("assessment_type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="iil_learnfw.assessmenttype", verbose_name="Assessment-Typ")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assessment_attempts", to=settings.AUTH_USER_MODEL, verbose_name="Benutzer")),
                ("maturity_level", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="iil_learnfw.assessmentmaturitylevel", verbose_name="Erreichter Reifegrad")),
            ],
            options={
                "verbose_name": "Assessment-Durchführung",
                "verbose_name_plural": "Assessment-Durchführungen",
                "ordering": ["-started_at"],
            },
        ),
        migrations.AddIndex(
            model_name="assessmentattempt",
            index=models.Index(
                fields=["assessment_type", "user", "tenant_id"],
                name="idx_attempt_type_user_tenant",
            ),
        ),
        migrations.AddIndex(
            model_name="assessmentattempt",
            index=models.Index(
                fields=["tenant_id", "deleted_at", "-started_at"],
                name="idx_attempt_tenant_deleted_date",
            ),
        ),
        migrations.AddIndex(
            model_name="assessmentattempt",
            index=models.Index(
                condition=models.Q(deleted_at__isnull=True),
                fields=["retention_expires_at"],
                name="idx_attempt_retention_active",
            ),
        ),
        migrations.AddConstraint(
            model_name="assessmentattempt",
            constraint=models.CheckConstraint(
                check=models.Q(total_pct__lte=100),
                name="assessment_attempt_total_pct_lte_100",
            ),
        ),
        # ------------------------------------------------------------------
        # AssessmentReport
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="AssessmentReport",
            fields=[
                ("tenant_id", models.UUIDField(blank=True, db_index=True, help_text="Tenant UUID (NULL = single-tenant mode or global content).", null=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("public_id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name="Public ID")),
                ("recommendations", models.JSONField(default=list, help_text="Snapshot zum Generierungszeitpunkt. Schema: [{dimension_key, gap_pct, title, description, priority, course_id, lesson_id, external_url}]", verbose_name="Empfehlungs-Snapshot")),
                ("pdf_file", models.FileField(blank=True, upload_to="assessments/reports/%Y/%m/", verbose_name="PDF-Datei")),
                ("generated_at", models.DateTimeField(auto_now_add=True, verbose_name="Generiert am")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Aktualisiert am")),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True, verbose_name="Gelöscht am")),
                ("attempt", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="report", to="iil_learnfw.assessmentattempt", verbose_name="Durchführung")),
                ("certificate", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="iil_learnfw.issuedcertificate", verbose_name="Ausgestelltes Zertifikat")),
            ],
            options={
                "verbose_name": "Assessment-Bericht",
                "verbose_name_plural": "Assessment-Berichte",
            },
        ),
    ]
