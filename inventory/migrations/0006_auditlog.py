from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0005_physicalinventory_is_pv_filled"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("create", "Creation"),
                            ("update", "Mise a jour"),
                            ("delete", "Suppression"),
                            ("import", "Import"),
                            ("close_year", "Cloture exercice"),
                            ("report_year", "Report exercice"),
                            ("login", "Connexion"),
                        ],
                        max_length=20,
                    ),
                ),
                ("entity", models.CharField(max_length=100)),
                ("entity_id", models.CharField(blank=True, max_length=100)),
                ("description", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                (
                    "fiscal_year",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audit_logs",
                        to="inventory.fiscalyear",
                    ),
                ),
                (
                    "structure",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audit_logs",
                        to="inventory.structure",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audit_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Journal d'audit",
                "verbose_name_plural": "Journal d'audit",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["created_at"], name="inventory_au_created_08eab8_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["action", "entity"], name="inventory_au_action_4d6b5f_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["structure", "fiscal_year"], name="inventory_au_structu_851dad_idx"),
        ),
    ]
