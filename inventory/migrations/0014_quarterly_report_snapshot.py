from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0013_quarterly_report"),
    ]

    operations = [
        migrations.AddField(
            model_name="quarterlyreport",
            name="snapshot_data",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
