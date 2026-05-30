import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compta_web.settings')
django.setup()

from inventory.models import PhysicalInventory, Material, InternalMovement, VoucherLine
from django.db.models import Sum, Q

print("=== PhysicalInventory Group 1 en 2026 (Sample) ===")
count = 0
for pi in PhysicalInventory.objects.filter(
    material__fiscal_year__year=2026, 
    material__group_code='1'
).select_related('material'):
    count += 1
    if count <= 3:  # Affiche seulement les 3 premiers
        print(f"\nMatériel: {pi.material.name} (ID={pi.material.id})")
        print(f"  is_pv_filled: {pi.is_pv_filled}")
        print(f"  pending_qty: {pi.pending_qty}, in_service_qty: {pi.in_service_qty}, provisional_qty: {pi.provisional_qty}")
print(f"\nTotal PhysicalInventory Group 1: {count}")

print("\n\n=== InternalMovement TYPE_ASSIGNMENT pour Group 1 en 2026 ===")
im_count = 0
for im in InternalMovement.objects.filter(
    fiscal_year__year=2026,
    movement_type=InternalMovement.TYPE_ASSIGNMENT
).prefetch_related('lines'):
    # Vérifier si une ligne concerne Group 1
    group1_lines = [line for line in im.lines.all() if line.material.group_code == '1']
    if group1_lines:
        im_count += 1
        if im_count <= 3:
            print(f"\nMouvement ID={im.id}, Date={im.operation_date}")
            for line in group1_lines:
                print(f"  - {line.material.name}: qty={line.quantity}")

if im_count == 0:
    print("AUCUN mouvement TYPE_ASSIGNMENT pour Group 1 en 2026!")
else:
    print(f"\nTotal mouvements TYPE_ASSIGNMENT: {im_count}")

print("\n\n=== VoucherLine pour Group 1 en 2026 (résumé) ===")
group1_voucher_lines = VoucherLine.objects.filter(
    voucher__fiscal_year__year=2026,
    material__group_code='1'
)
print(f"Total VoucherLine Group 1: {group1_voucher_lines.count()}")
print(f"  ENTRY (entree): {group1_voucher_lines.filter(voucher__voucher_type='entree').count()}")
print(f"  FINAL_EXIT (sortie_definitive): {group1_voucher_lines.filter(voucher__voucher_type='sortie_definitive').count()}")
print(f"  TEMP_EXIT (sortie_provisoire): {group1_voucher_lines.filter(voucher__voucher_type='sortie_provisoire').count()}")
