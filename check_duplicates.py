import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compta_web.settings')
django.setup()

from inventory.models import Material, Structure, FiscalYear

print("=== Tous les Materials 'Table Bureau Ministre' en 2026 ===\n")

fy_2026 = FiscalYear.objects.filter(year=2026).first()

materials = Material.objects.filter(
    name='Table Bureau Ministre',
    fiscal_year=fy_2026
).select_related('structure')

for m in materials:
    pi = getattr(m, 'physical_inventory', None)
    print(f"ID={m.id:<4} Structure={m.structure.name:<60} account_code={m.account_code}")
    print(f"      PhysicalInventory: {'YES' if pi else 'NO':<3}")
    if pi:
        print(f"      pending={pi.pending_qty}, in_service={pi.in_service_qty}")
    print()

print("\n=== Vérifier les mouvements d'affectation pour ce Material ===")
from inventory.models import InternalMovement

print("\nMatériau ID=24 (utilisé par le relevé):")
movements = InternalMovement.objects.filter(
    fiscal_year=fy_2026,
    movement_type=InternalMovement.TYPE_ASSIGNMENT
).prefetch_related('lines')

for im in movements:
    for line in im.lines.all():
        if line.material_id == 24:
            print(f"  Mouvement {im.id}: qty={line.quantity}")

print("\nMatériau ID=73 (a PhysicalInventory avec in_service=1):")
for im in movements:
    for line in im.lines.all():
        if line.material_id == 73:
            print(f"  Mouvement {im.id}: qty={line.quantity}")
