import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compta_web.settings')
django.setup()

from inventory.models import Structure, FiscalYear
from inventory.services import compute_stock_summary

# Récupérer Dakar
dakar_structure = Structure.objects.filter(name__contains='Dakar').first()
fy_2026 = FiscalYear.objects.filter(year=2026, structure=dakar_structure).first()

if not (dakar_structure and fy_2026):
    print(f"Dakar structure: {dakar_structure}")
    print(f"FiscalYear 2026: {fy_2026}")
    exit(1)

print(f"=== Relevé Récapitulatif pour {dakar_structure.name} - Exercice 2026 ===\n")

# Générer le relevé
rows = compute_stock_summary(dakar_structure, fy_2026)

# Filtrer Group 1 et matériaux ayant des mouvements d'affectation
group1_rows = [r for r in rows if r.group_code == '1']

print(f"{'Code':<10} {'Matériel':<45} {'Attente':<10} {'Service':<10} {'Prov.':<10}")
print("-" * 95)

# Matériaux affectés: Table Bureau Ministre, Armoire, Climatiseur, Fauteuil, Chaises
affected_codes = ['10 01 01', '10 02 01', '10 03 01', '10 04 01', '10 07 01']

total_pending = 0
total_in_service = 0

for row in group1_rows:
    if row.account_code in affected_codes:
        print(f"{row.account_code:<10} {row.name:<45} {row.pending_qty:>9} {row.in_service_qty:>9} {row.provisional_qty:>9}")
        total_pending += row.pending_qty
        total_in_service += row.in_service_qty

print("-" * 95)
print(f"{'TOTAL':<55} {total_pending:>9} {total_in_service:>9}")

print("\n=== Attendus (depuis les mouvements d'affectation) ===")
print("Table Bureau Ministre: 1 affectée (Mouvement 1)")
print("Armoire de bureau: 3 affectées (Mouvements 1, 2, 3)")
print("Climatiseur: 2 affectés (Mouvements 1, 2)")
print("Fauteuil: 1 affecté (Mouvement 3)")
print("Chaises: 10 affectées (Mouvements 1: 4 + 2: 4 + 3: 2)")
