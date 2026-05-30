import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compta_web.settings')
django.setup()

from inventory.models import Structure, FiscalYear
from inventory.services import compute_stock_summary

# Récupérer structure et année 2026
fy_2026 = FiscalYear.objects.filter(year=2026).first()
structure = fy_2026.structure if fy_2026 else None

if not (structure and fy_2026):
    print("Erreur: Structure ou FiscalYear 2026 non trouvés")
    exit(1)

print(f"=== Relevé Récapitulatif pour {structure.name} - Exercice 2026 ===\n")

# Générer le relevé
rows = compute_stock_summary(structure, fy_2026)

# Filtrer Group 1
group1_rows = [r for r in rows if r.group_code == '1']

print(f"{'Code':<10} {'Matériel':<40} {'Attente':<12} {'En Service':<12} {'Provision.':<12} {'Total':<12}")
print("-" * 100)

total_pending = 0
total_in_service = 0
total_provisional = 0

for row in group1_rows[:10]:  # Premiers 10 pour éviter le spam
    print(f"{row.account_code:<10} {row.name:<40} {row.pending_qty:>11} {row.in_service_qty:>11} {row.provisional_qty:>11} {row.inventory_total_qty:>11}")
    total_pending += row.pending_qty
    total_in_service += row.in_service_qty
    total_provisional += row.provisional_qty

print("-" * 100)
print(f"{'TOTAL':<50} {total_pending:>11} {total_in_service:>11} {total_provisional:>11} {total_pending + total_in_service + total_provisional:>11}")
