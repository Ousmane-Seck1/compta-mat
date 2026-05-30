import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compta_web.settings')
django.setup()

from inventory.models import Material, PhysicalInventory

print("=== Créer PhysicalInventory manquants ===\n")

# Trouver tous les Materials sans PhysicalInventory
materials_without_pi = Material.objects.filter(physical_inventory__isnull=True)

created_count = 0
for material in materials_without_pi:
    # Créer un PhysicalInventory avec les bonnes quantités
    pi = PhysicalInventory.objects.create(
        material=material,
        pending_qty=0,
        in_service_qty=0,
        provisional_qty=0,
        unit_price=0,
        is_pv_filled=False
    )
    created_count += 1
    if created_count <= 10:  # Afficher seulement les 10 premiers
        print(f"✓ Créé PhysicalInventory pour {material.name} (Material ID={material.id})")

print(f"\nTotal PhysicalInventory créés: {created_count}")
