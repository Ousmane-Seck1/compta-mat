from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0009_alter_fiscalyear_options_alter_material_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="voucher",
            name="temp_return_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="voucher",
            name="temp_return_note",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
