from django.db import migrations, models


def populate_nomenclature_from_materials(apps, schema_editor):
    """Populate NomenclatureItem from the distinct account codes already in Material."""
    Material = apps.get_model('inventory', 'Material')
    NomenclatureItem = apps.get_model('inventory', 'NomenclatureItem')
    seen = set()
    for mat in Material.objects.order_by('account_code'):
        if mat.account_code and mat.account_code not in seen:
            NomenclatureItem.objects.get_or_create(
                account_code=mat.account_code,
                defaults={
                    'name': mat.name,
                    'unit': mat.unit,
                    'group_code': mat.group_code,
                },
            )
            seen.add(mat.account_code)


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_structure_logo'),
    ]

    operations = [
        migrations.CreateModel(
            name='NomenclatureItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account_code', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('unit', models.CharField(max_length=20)),
                ('group_code', models.CharField(blank=True, max_length=10)),
            ],
            options={
                'verbose_name': 'Compte de nomenclature',
                'verbose_name_plural': 'Comptes de nomenclature',
                'ordering': ['account_code'],
            },
        ),
        migrations.RunPython(
            code=populate_nomenclature_from_materials,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
