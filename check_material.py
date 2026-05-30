import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compta_web.settings')
django.setup()

from inventory.models import Material, VoucherLine, FiscalYear, Structure
from django.db.models import Sum

print("=== Table Bureau Ministre - Tous les ID par Exercice ===\n")

materials = Material.objects.filter(name='Table Bureau Ministre').order_by('fiscal_year__year', 'id')

for m in materials:
    fy_year = m.fiscal_year.year if m.fiscal_year else '?'
    pi = getattr(m, 'physical_inventory', None)
    if pi:
        print(f"ID={m.id:<4} Année={fy_year} pending={pi.pending_qty} in_service={pi.in_service_qty}")
    else:
        print(f"ID={m.id:<4} Année={fy_year} (pas de PhysicalInventory)")
    
    # Afficher aussi les bons d'entrée
    entries = VoucherLine.objects.filter(material=m, voucher__voucher_type='entree')
    total_qty = entries.aggregate(total=Sum('quantity'))['total'] or 0
    print(f"      → VoucherLine ENTRY count={entries.count()}, total_qty={total_qty}")

print("\n=== Vérifier quel Material est utilisé pour le relevé 2026 ===")

fy_2026 = FiscalYear.objects.filter(year=2026).first()
structure = fy_2026.structure if fy_2026 else None

table_in_2026 = Material.objects.filter(
    name='Table Bureau Ministre',
    fiscal_year=fy_2026,
    structure=structure
).first()

if table_in_2026:
    print(f"\nMaterial pour compute_stock_summary: ID={table_in_2026.id}")
    pi = getattr(table_in_2026, 'physical_inventory', None)
    if pi:
        print(f"  PhysicalInventory: pending={pi.pending_qty}, in_service={pi.in_service_qty}, provisional={pi.provisional_qty}")
    
    # Bons
    total_entry = VoucherLine.objects.filter(
        material=table_in_2026,
        voucher__voucher_type='entree'
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    total_exit = VoucherLine.objects.filter(
        material=table_in_2026,
        voucher__voucher_type__in=['sortie_definitive', 'sortie_provisoire']
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    remaining = total_entry - total_exit
    print(f"  Bons: ENTRY total={total_entry}, EXIT total={total_exit}, remaining={remaining}")
