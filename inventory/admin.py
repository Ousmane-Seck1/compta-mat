from __future__ import annotations

from django.contrib import admin

from .models import (
    AuditLog,
    FiscalYear,
    InternalMovement,
    InternalMovementLine,
    Location,
    Material,
    NomenclatureItem,
    PhysicalInventory,
    SiteSetting,
    Structure,
    UserProfile,
    Voucher,
    VoucherLine,
)


admin.site.site_header = "Comptabilité des matières"
admin.site.site_title = "Comptabilité des matières"
admin.site.index_title = "Gestion de la comptabilité des matières"


class VoucherLineInline(admin.TabularInline):
    model = VoucherLine
    extra = 0


class InternalMovementLineInline(admin.TabularInline):
    model = InternalMovementLine
    extra = 0


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "region", "logo", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "region")
    fields = ("code", "name", "region", "logo", "is_active")


@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ("__str__", "year", "start_date", "end_date", "is_active", "is_closed")
    list_filter = ("structure", "year", "is_active", "is_closed")
    search_fields = ("structure__code", "structure__name")
    fields = ("structure", "year", "start_date", "end_date", "is_active", "is_closed")


class VoucherAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "voucher_type",
        "operation_date",
        "temp_return_status_label",
        "temp_return_date",
        "source_or_destination",
        "structure",
        "fiscal_year",
        "created_by",
    )
    list_filter = ("structure", "fiscal_year", "voucher_type", "operation_date")
    search_fields = ("number", "source_or_destination")
    fields = (
        "structure",
        "fiscal_year",
        "number",
        "voucher_type",
        "operation_date",
        "source_or_destination",
        "comments",
        "temp_return_date",
        "temp_return_note",
        "created_by",
    )
    inlines = [VoucherLineInline]
    readonly_fields = ("created_by",)


class MaterialAdmin(admin.ModelAdmin):
    list_display = ("account_code", "name", "unit", "group_code", "structure", "fiscal_year")
    search_fields = ("account_code", "name")
    list_filter = ("group_code", "structure", "fiscal_year")
    fields = ("structure", "fiscal_year", "account_code", "name", "unit", "group_code")


class PhysicalInventoryAdmin(admin.ModelAdmin):
    list_display = ("material", "pending_qty", "in_service_qty", "provisional_qty", "unit_price", "updated_at")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "location_type", "structure", "responsible_name", "is_active")
    list_filter = ("structure", "location_type", "is_active")
    search_fields = ("name", "responsible_name", "details")
    fields = ("structure", "name", "location_type", "responsible_name", "details", "is_active")


@admin.register(InternalMovement)
class InternalMovementAdmin(admin.ModelAdmin):
    list_display = ("number", "movement_type", "operation_date", "from_location", "to_location", "structure", "fiscal_year")
    list_filter = ("structure", "fiscal_year", "movement_type", "operation_date")
    search_fields = ("number", "from_location__name", "to_location__name", "reason")
    fields = ("structure", "fiscal_year", "number", "movement_type", "operation_date", "from_location", "to_location", "reason", "created_by")
    readonly_fields = ("created_by",)
    inlines = [InternalMovementLineInline]


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
    search_fields = ("key", "value")

    def has_add_permission(self, request):  # noqa: ANN001
        return False

    def has_change_permission(self, request, obj=None):  # noqa: ANN001
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ANN001
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "entity", "entity_id", "user", "structure", "fiscal_year")
    list_filter = ("action", "entity", "structure", "fiscal_year", "created_at")
    search_fields = ("entity", "entity_id", "description", "user__username")
    readonly_fields = (
        "created_at",
        "updated_at",
        "action",
        "entity",
        "entity_id",
        "description",
        "metadata",
        "user",
        "structure",
        "fiscal_year",
    )

    def has_add_permission(self, request):  # noqa: ANN001
        return False

    def has_change_permission(self, request, obj=None):  # noqa: ANN001
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ANN001
        return False


@admin.register(NomenclatureItem)
class NomenclatureItemAdmin(admin.ModelAdmin):
    list_display = ("account_code", "name", "unit", "group_code")
    search_fields = ("account_code", "name", "group_code")
    fields = ("account_code", "name", "unit", "group_code")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "display_name", "default_structure")
    list_filter = ("role", "default_structure")
    search_fields = ("user__username", "display_name")
    fields = ("user", "role", "display_name", "default_structure", "assigned_structures")
    filter_horizontal = ("assigned_structures",)
