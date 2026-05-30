import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compta_web.settings')
django.setup()

from inventory.models import Material, FiscalYear

print("=== Tous les Materials 'Table Bureau Ministre' en 2026 avec Structures ===\n")

fy_2026_list = FiscalYear.objects.filter(year=2026)

for fy in fy_2026_list:
    print(f"\n--- FiscalYear 2026 pour {fy.structure.name} ---")
    
    materials = Material.objects.filter(
        name='Table Bureau Ministre',
        fiscal_year=fy
    )
    
    if not materials.exists():
        print("  Aucun Material")
    else:
        for m in materials:
            pi = getattr(m, 'physical_inventory', None)
            print(f"  ID={m.id}: PhysicalInventory={'YES' if pi else 'NO'}")
            if pi:
                print(f"         in_service_qty={pi.in_service_qty}")

print("\n\n=== Vérifier tous les InternalMovement en 2026 ===")
from inventory.models import InternalMovement

for fy in fy_2026_list:
    movements = InternalMovement.objects.filter(
        fiscal_year=fy,
        movement_type=InternalMovement.TYPE_ASSIGNMENT
    ).prefetch_related('lines')
    
    print(f"\n{fy.structure.name}: {movements.count()} mouvements d'affectation")
    for im in movements:
        print(f"  Mouvement {im.id}:")
        for line in im.lines.all():
            print(f"    - {line.material.name} (ID={line.material.id}): qty={line.quantity}")
