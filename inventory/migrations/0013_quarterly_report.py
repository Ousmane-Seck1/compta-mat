from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0012_voucher_storage_location"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuarterlyReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("quarter", models.PositiveSmallIntegerField()),
                ("name", models.CharField(max_length=120)),
                ("pdf_file", models.FileField(blank=True, upload_to="quarterly_reports/")),
                ("excel_file", models.FileField(blank=True, upload_to="quarterly_reports/")),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="quarterly_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "fiscal_year",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quarterly_reports",
                        to="inventory.fiscalyear",
                    ),
                ),
                (
                    "structure",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quarterly_reports",
                        to="inventory.structure",
                    ),
                ),
            ],
            options={
                "verbose_name": "Rapport trimestriel",
                "verbose_name_plural": "Rapports trimestriels",
                "ordering": ["-created_at"],
                "unique_together": {("structure", "fiscal_year", "quarter")},
            },
        ),
    ]
