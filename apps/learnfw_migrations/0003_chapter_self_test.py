"""Fehlende Migration für ``Chapter.self_test`` (iil_learnfw 0.5.x).

Das learnfw-Paket-Modell führte ``Chapter.self_test`` (JSONField) ein; learn-hub
ist Migrations-Owner der Shared DB (MIGRATION_MODULES → apps.learnfw_migrations),
aber die zugehörige Migration wurde nie generiert. Folge: Prod-DB ohne die Spalte
→ jede Chapter-Operation bricht (``column ... self_test does not exist``). CI
übersah es, weil Unit-Tests mit ``--no-migrations`` die Test-DB aus den Modellen
bauen. Diese Migration schließt die Lücke; das neue makemigrations-Gate (ci.yml)
verhindert die Wiederholung. Rein additiv, reversibel.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("iil_learnfw", "0002_assessment_engine"),
    ]

    operations = [
        migrations.AddField(
            model_name="chapter",
            name="self_test",
            field=models.JSONField(
                blank=True,
                help_text='[{"question":"...","expected":"...","keywords":["k1"]}]',
                null=True,
            ),
        ),
    ]
