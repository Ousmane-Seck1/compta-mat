from __future__ import annotations

from collections import defaultdict

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from inventory.models import FiscalYear, InternalMovement, InternalMovementLine, Location, Material, Structure
from inventory.services import (
    ZERO,
    _create_internal_movement_header_with_retry,
    _expected_store_location_type,
    _resolve_voucher_store_for_materials,
    build_location_inventory_report,
)


User = get_user_model()


class Command(BaseCommand):
    help = "Report location inventory (per bureau) into a new fiscal year as internal movements."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--structure-code", required=True, help="Structure code (e.g., 'DRS DK').")
        parser.add_argument("--from-year", type=int, required=True, help="Source fiscal year.")
        parser.add_argument("--to-year", type=int, required=True, help="Target fiscal year.")
        parser.add_argument("--user", default="", help="Username to set as created_by.")
        parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run).")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Allow applying even if target year already has internal movements.",
        )

    def handle(self, *args, **options):
        code = options["structure_code"].strip()
        from_year = int(options["from_year"])
        to_year = int(options["to_year"])
        apply_changes = bool(options["apply"])
        force = bool(options["force"])
        username = options["user"].strip()

        structure = Structure.objects.filter(code=code).first()
        if not structure:
            self.stdout.write(self.style.ERROR(f"Structure introuvable: {code}"))
            return

        from_fy = FiscalYear.objects.filter(structure=structure, year=from_year).first()
        if not from_fy:
            self.stdout.write(self.style.ERROR(f"Exercice source introuvable: {from_year}"))
            return

        to_fy = FiscalYear.objects.filter(structure=structure, year=to_year).first()
        if not to_fy:
            self.stdout.write(self.style.ERROR(f"Exercice cible introuvable: {to_year}"))
            return

        if InternalMovement.objects.filter(structure=structure, fiscal_year=to_fy).exists() and not force:
            self.stdout.write(
                self.style.ERROR(
                    "Des bordereaux internes existent deja sur l'exercice cible. "
                    "Relancez avec --force pour continuer."
                )
            )
            return

        created_by = None
        if username:
            created_by = User.objects.filter(username=username).first()
            if created_by is None:
                self.stdout.write(self.style.ERROR(f"Utilisateur introuvable: {username}"))
                return

        material_map: dict[str, Material] = {}
        for material in Material.objects.filter(structure=structure, fiscal_year=to_fy):
            material_map[material.account_code] = material

        locations = Location.objects.filter(structure=structure).order_by("name")
        moves_preview = []

        for location in locations:
            if location.is_store:
                continue
            rows = build_location_inventory_report(location, from_fy)
            if not rows:
                continue

            lines_by_store_type: dict[str, list[tuple[Material, object]]] = defaultdict(list)
            for row in rows:
                if row.quantity <= ZERO:
                    continue
                old_material = Material.objects.filter(pk=row.material_id).first()
                if not old_material:
                    continue
                new_material = material_map.get(old_material.account_code)
                if not new_material:
                    continue
                store_type = _expected_store_location_type(old_material)
                lines_by_store_type[store_type].append((new_material, row))

            for store_type, group in lines_by_store_type.items():
                moves_preview.append((location, store_type, group))

        if not apply_changes:
            self.stdout.write(
                self.style.NOTICE(
                    f"{len(moves_preview)} bordereau(x) seront crees pour {code} {from_year} -> {to_year}."
                )
            )
            for location, store_type, group in moves_preview:
                total_qty = sum((row.quantity for _, row in group), ZERO)
                self.stdout.write(
                    f"- {location.name} ({store_type}): {len(group)} lignes, qte {total_qty}"
                )
            self.stdout.write(self.style.NOTICE("Dry-run uniquement. Relancez avec --apply pour appliquer."))
            return

        self._apply_report(moves_preview, structure, from_fy, to_fy, created_by)

    @transaction.atomic
    def _apply_report(self, moves_preview, structure, from_fy, to_fy, created_by) -> None:
        created = 0
        for location, _store_type, group in moves_preview:
            materials = [item[0] for item in group]
            expected_store = _resolve_voucher_store_for_materials(
                materials=materials,
                structure=structure,
            )
            movement = _create_internal_movement_header_with_retry(
                structure=structure,
                fiscal_year=to_fy,
                movement_type=InternalMovement.TYPE_ASSIGNMENT,
                operation_date=to_fy.start_date,
                from_location=expected_store,
                to_location=location,
                reason=f"Report des affectations depuis {from_fy.year}",
                created_by=created_by,
            )
            for new_material, row in group:
                amount = row.quantity * row.unit_price
                InternalMovementLine.objects.create(
                    movement=movement,
                    material=new_material,
                    material_name=new_material.name,
                    inventory_code=row.inventory_code,
                    quantity=row.quantity,
                    unit=new_material.unit,
                    unit_price=row.unit_price,
                    amount=amount,
                    observations="Report affectation exercice precedent",
                )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Report termine: {created} bordereau(x) crees pour {structure.code} {from_fy.year}->{to_fy.year}."
            )
        )
