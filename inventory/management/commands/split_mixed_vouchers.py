from __future__ import annotations

from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from inventory.models import FiscalYear, Voucher, VoucherLine
from inventory.services import _account_prefix, _resolve_voucher_store_for_materials, next_voucher_number


class Command(BaseCommand):
    help = "Split vouchers that mix equipment (1) and supplies (2) lines by store type."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--year",
            type=int,
            default=2026,
            help="Fiscal year to process (default: 2026).",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply changes (default is dry-run).",
        )

    def handle(self, *args, **options):
        year = int(options["year"])
        apply_changes = bool(options["apply"])

        self.stdout.write(self.style.NOTICE(f"Scanning vouchers for fiscal year {year}..."))
        fiscal_years = FiscalYear.objects.filter(year=year).select_related("structure")
        if not fiscal_years.exists():
            self.stdout.write(self.style.WARNING("No fiscal years found."))
            return

        total_scanned = 0
        total_mixed = 0
        total_split = 0

        for fy in fiscal_years:
            vouchers = (
                Voucher.objects.filter(fiscal_year=fy)
                .select_related("structure")
                .prefetch_related("lines__material")
                .order_by("number")
            )
            for voucher in vouchers:
                total_scanned += 1
                prefixes = {(_account_prefix(line.material) or "") for line in voucher.lines.all()}
                prefixes.discard("")
                if not {"1", "2"}.issubset(prefixes):
                    continue

                total_mixed += 1
                if not apply_changes:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Mixed voucher found: FY {fy.year} / {fy.structure.code} / N° {voucher.number}"
                        )
                    )
                    continue

                total_split += self._split_voucher(voucher)

        self.stdout.write(
            self.style.SUCCESS(
                f"Scanned {total_scanned} vouchers. Mixed: {total_mixed}. Split: {total_split}."
            )
        )

        if not apply_changes:
            self.stdout.write(self.style.NOTICE("Dry-run only. Re-run with --apply to split."))

    @transaction.atomic
    def _split_voucher(self, voucher: Voucher) -> int:
        fy = voucher.fiscal_year
        structure = voucher.structure

        lines_by_prefix: dict[str, list[VoucherLine]] = defaultdict(list)
        for line in voucher.lines.all():
            prefix = _account_prefix(line.material)
            if prefix in {"1", "2"}:
                lines_by_prefix[prefix].append(line)

        created = 0
        for prefix, lines in lines_by_prefix.items():
            materials = [line.material for line in lines]
            expected_store = _resolve_voucher_store_for_materials(
                materials=materials,
                structure=structure,
            )
            new_number = next_voucher_number(structure, fy)
            new_voucher = Voucher.objects.create(
                structure=structure,
                fiscal_year=fy,
                number=new_number,
                voucher_type=voucher.voucher_type,
                operation_date=voucher.operation_date,
                source_or_destination=voucher.source_or_destination,
                storage_location=expected_store,
                comments=voucher.comments,
                temp_return_date=voucher.temp_return_date,
                temp_return_note=voucher.temp_return_note,
                created_by=voucher.created_by,
            )

            VoucherLine.objects.filter(id__in=[line.id for line in lines]).update(voucher=new_voucher)
            created += 1

        voucher.delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Split voucher FY {fy.year} / {structure.code} / N° {voucher.number} into {created} vouchers."
            )
        )
        return created
