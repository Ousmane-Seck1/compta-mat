from __future__ import annotations

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0011_internalmovement_internalmovementline_location_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="voucher",
            name="storage_location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="vouchers",
                to="inventory.location",
            ),
        ),
    ]
