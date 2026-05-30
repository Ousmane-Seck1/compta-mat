from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0006_auditlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="structure",
            name="logo",
            field=models.FileField(blank=True, upload_to="structure_logos/"),
        ),
    ]
