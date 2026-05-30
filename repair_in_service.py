import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compta_web.settings')
django.setup()

from inventory.models import PhysicalInventory, Material, InternalMovement, FiscalYear
from decimal import Decimal

# Recalculer in_service_qty pour 2026
print("=== Recalcul de in_service_qty pour 2026 ===\n")

# Pour chaque matériau Group 1 en 2026
materials_2026_g1 = Material.objects.filter(
    fiscal_year__year=2026,
    group_code='1'
).select_related('fiscal_year')

updated_count = 0
for material in materials_2026_g1:
    physical = getattr(material, 'physical_inventory', None)
    if not physical:
        continue
    
    # Calculer in_service_qty depuis les mouvements d'affectation
    # = somme des AFFECTATIONS (TYPE_ASSIGNMENT) - somme des DESAFFECTATIONS (TYPE_UNASSIGNMENT)
    
    # Récupérer tous les mouvements d'affectation et de désaffectation pour ce matériau
    assigned_qty = Decimal('0')  # TYPE_ASSIGNMENT
    unassigned_qty = Decimal('0')  # TYPE_UNASSIGNMENT
    
    for im in InternalMovement.objects.filter(
        fiscal_year=material.fiscal_year,
        movement_type=InternalMovement.TYPE_ASSIGNMENT
    ).prefetch_related('lines'):
        for line in im.lines.all():
            if line.material_id == material.id:
                assigned_qty += line.quantity
    
    for im in InternalMovement.objects.filter(
        fiscal_year=material.fiscal_year,
        movement_type=InternalMovement.TYPE_UNASSIGNMENT
    ).prefetch_related('lines'):
        for line in im.lines.all():
            if line.material_id == material.id:
                unassigned_qty += line.quantity
    
    new_in_service_qty = assigned_qty - unassigned_qty
    
    if new_in_service_qty != physical.in_service_qty:
        old_value = physical.in_service_qty
        physical.in_service_qty = new_in_service_qty
        physical.save(update_fields=['in_service_qty'])
        print(f"✓ {material.name} (ID={material.id})")
        print(f"  in_service_qty: {old_value} → {new_in_service_qty}")
        updated_count += 1

print(f"\nTotal matériaux mis à jour: {updated_count}")
