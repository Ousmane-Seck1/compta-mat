from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Structure(TimeStampedModel):
    """Service, district sanitaire ou centre de responsabilité."""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    region = models.CharField(max_length=255, blank=True)
    logo = models.FileField(upload_to="structure_logos/", blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class FiscalYear(TimeStampedModel):
    """Exercice comptable (année fiscale)."""
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name="fiscal_years")
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-year"]
        unique_together = [("structure", "year")]
        indexes = [models.Index(fields=["structure", "year"])]
        verbose_name = "Exercice"
        verbose_name_plural = "Exercices"

    def __str__(self) -> str:
        return f"{self.structure.code} - {self.year}"


class SiteSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)

    class Meta:
        ordering = ["key"]
        verbose_name = "Parametre"
        verbose_name_plural = "Parametres"

    def __str__(self) -> str:
        return f"{self.key}={self.value}"


class NomenclatureItem(TimeStampedModel):
    """Referentiel global des comptes de matieres, gere par l'admin uniquement."""
    account_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=20)
    group_code = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ["account_code"]
        verbose_name = "Compte de nomenclature"
        verbose_name_plural = "Comptes de nomenclature"

    def __str__(self) -> str:
        return f"{self.account_code} - {self.name}"


class Material(TimeStampedModel):
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name="materials", null=True, blank=False)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name="materials", null=True, blank=False)
    account_code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=20)
    group_code = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ["account_code"]
        unique_together = [("structure", "fiscal_year", "account_code")]
        indexes = [
            models.Index(fields=["structure", "fiscal_year", "account_code"]),
            models.Index(fields=["structure", "fiscal_year"]),
        ]
        verbose_name = "Matiere"
        verbose_name_plural = "Matieres"

    def __str__(self) -> str:
        return f"{self.account_code} - {self.name}"


class Voucher(TimeStampedModel):
    TYPE_ENTRY = "entree"
    TYPE_FINAL_EXIT = "sortie_definitive"
    TYPE_TEMP_EXIT = "sortie_provisoire"
    TYPE_CHOICES = [
        (TYPE_ENTRY, "Bon d'entree"),
        (TYPE_FINAL_EXIT, "Bon de sortie definitive"),
        (TYPE_TEMP_EXIT, "Bon de sortie provisoire"),
    ]

    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name="vouchers", null=True, blank=False)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name="vouchers", null=True, blank=False)
    number = models.PositiveIntegerField()
    voucher_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    operation_date = models.DateField()
    source_or_destination = models.CharField(max_length=255, blank=True)
    storage_location = models.ForeignKey(
        "Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vouchers",
    )
    comments = models.TextField(blank=True)
    temp_return_date = models.DateField(null=True, blank=True)
    temp_return_note = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_vouchers",
    )

    class Meta:
        ordering = ["-operation_date", "-number"]
        unique_together = [("structure", "fiscal_year", "number")]
        indexes = [
            models.Index(fields=["structure", "fiscal_year", "number"]),
            models.Index(fields=["structure", "fiscal_year", "operation_date"]),
        ]
        verbose_name = "Bon"
        verbose_name_plural = "Bons"

    def __str__(self) -> str:
        return f"Bon {self.number}"

    @property
    def total_amount(self) -> Decimal:
        return sum((line.amount for line in self.lines.all()), Decimal("0"))

    @property
    def temp_return_status(self) -> str:
        if self.voucher_type != self.TYPE_TEMP_EXIT:
            return ""
        return "retourne" if self.temp_return_date else "en_cours"

    @property
    def temp_return_status_label(self) -> str:
        if self.voucher_type != self.TYPE_TEMP_EXIT:
            return ""
        return "Retourne" if self.temp_return_date else "En cours"


class VoucherLine(models.Model):
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name="lines")
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="voucher_lines")
    material_name = models.CharField(max_length=255)
    specification = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    amount = models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:
        ordering = ["id"]
        verbose_name = "Ligne de bon"
        verbose_name_plural = "Lignes de bon"

    def __str__(self) -> str:
        return f"{self.material_name} ({self.quantity})"


class PhysicalInventory(TimeStampedModel):
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name="physical_inventory")
    pending_qty = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    in_service_qty = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    provisional_qty = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_pv_filled = models.BooleanField(default=False)

    class Meta:
        ordering = ["material__account_code"]
        verbose_name = "Proces verbal de recensement"
        verbose_name_plural = "Proces verbaux de recensement"

    def __str__(self) -> str:
        return f"PV {self.material.account_code}"


class Location(TimeStampedModel):
    TYPE_STORE_EQUIPMENT = "store_equipment"
    TYPE_STORE_SUPPLIES = "store_supplies"
    TYPE_STORE_PRODUCTS = "store_products"
    TYPE_OFFICE = "office"
    TYPE_ROOM = "room"
    TYPE_VEHICLE_PARK = "vehicle_park"
    TYPE_OTHER = "other"
    TYPE_CHOICES = [
        (TYPE_STORE_EQUIPMENT, "Magasin de materiel et equipement"),
        (TYPE_STORE_SUPPLIES, "Magasin de matieres et fournitures"),
        (TYPE_STORE_PRODUCTS, "Magasin de produits"),
        (TYPE_OFFICE, "Bureau"),
        (TYPE_ROOM, "Salle"),
        (TYPE_VEHICLE_PARK, "Parc auto"),
        (TYPE_OTHER, "Autre localisation"),
    ]

    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=255)
    location_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=TYPE_OTHER)
    responsible_name = models.CharField(max_length=255, blank=True)
    details = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("structure", "name")]
        indexes = [models.Index(fields=["structure", "location_type", "name"])]
        verbose_name = "Localisation"
        verbose_name_plural = "Localisations"

    def __str__(self) -> str:
        return self.name

    @property
    def is_store(self) -> bool:
        return self.location_type in {
            self.TYPE_STORE_EQUIPMENT,
            self.TYPE_STORE_SUPPLIES,
            self.TYPE_STORE_PRODUCTS,
        }


class InternalMovement(TimeStampedModel):
    TYPE_ASSIGNMENT = "affectation"
    TYPE_TRANSFER = "mutation"
    TYPE_UNASSIGNMENT = "desaffectation"
    TYPE_CHOICES = [
        (TYPE_ASSIGNMENT, "Affectation"),
        (TYPE_TRANSFER, "Mutation"),
        (TYPE_UNASSIGNMENT, "Desaffectation"),
    ]

    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name="internal_movements")
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name="internal_movements")
    number = models.PositiveIntegerField()
    movement_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    operation_date = models.DateField()
    from_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="outgoing_internal_movements",
    )
    to_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="incoming_internal_movements",
    )
    reason = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_internal_movements",
    )

    class Meta:
        ordering = ["-operation_date", "-number"]
        unique_together = [("structure", "fiscal_year", "number")]
        indexes = [
            models.Index(fields=["structure", "fiscal_year", "number"]),
            models.Index(fields=["structure", "fiscal_year", "operation_date"]),
        ]
        verbose_name = "Bordereau interne"
        verbose_name_plural = "Bordereaux internes"

    def __str__(self) -> str:
        return f"Bordereau interne {self.number}"

    @property
    def total_amount(self) -> Decimal:
        return sum((line.amount for line in self.lines.all()), Decimal("0"))


class InternalMovementLine(models.Model):
    movement = models.ForeignKey(InternalMovement, on_delete=models.CASCADE, related_name="lines")
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="internal_movement_lines")
    material_name = models.CharField(max_length=255)
    inventory_code = models.CharField(max_length=100, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    observations = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Ligne de bordereau interne"
        verbose_name_plural = "Lignes de bordereau interne"

    def __str__(self) -> str:
        return f"{self.material_name} ({self.quantity})"


class UserProfile(TimeStampedModel):
    ROLE_ADMIN = "admin"
    ROLE_ACCOUNTANT = "comptable"
    ROLE_VIEWER = "consultation"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Administrateur (tous les services)"),
        (ROLE_ACCOUNTANT, "Comptable matieres"),
        (ROLE_VIEWER, "Consultation"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_VIEWER)
    display_name = models.CharField(max_length=150, blank=True)
    default_structure = models.ForeignKey(
        Structure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="default_users",
        help_text="Structure par defaut apres connexion. Admin a acces a tous les services.",
    )
    assigned_structures = models.ManyToManyField(
        Structure,
        blank=True,
        related_name="assigned_users",
        help_text="Structures autorisees pour cet utilisateur (ignoree si admin).",
    )

    class Meta:
        ordering = ["user__username"]
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self) -> str:
        return self.display_name or self.user.get_username()


class AuditLog(TimeStampedModel):
    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_DELETE = "delete"
    ACTION_IMPORT = "import"
    ACTION_CLOSE_YEAR = "close_year"
    ACTION_REPORT_YEAR = "report_year"
    ACTION_LOGIN = "login"
    ACTION_CHOICES = [
        (ACTION_CREATE, "Creation"),
        (ACTION_UPDATE, "Mise a jour"),
        (ACTION_DELETE, "Suppression"),
        (ACTION_IMPORT, "Import"),
        (ACTION_CLOSE_YEAR, "Cloture exercice"),
        (ACTION_REPORT_YEAR, "Report exercice"),
        (ACTION_LOGIN, "Connexion"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    structure = models.ForeignKey(
        Structure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    fiscal_year = models.ForeignKey(
        FiscalYear,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["action", "entity"]),
            models.Index(fields=["structure", "fiscal_year"]),
        ]
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journal d'audit"

    def __str__(self) -> str:
        user = self.user.get_username() if self.user else "system"
        return f"{self.created_at:%Y-%m-%d %H:%M} - {self.action} - {self.entity} ({user})"


class QuarterlyReport(TimeStampedModel):
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name="quarterly_reports")
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name="quarterly_reports")
    quarter = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=120)
    pdf_file = models.FileField(upload_to="quarterly_reports/", blank=True)
    excel_file = models.FileField(upload_to="quarterly_reports/", blank=True)
    snapshot_data = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quarterly_reports",
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("structure", "fiscal_year", "quarter")]
        verbose_name = "Rapport trimestriel"
        verbose_name_plural = "Rapports trimestriels"

    def __str__(self) -> str:
        return f"{self.structure.code} {self.fiscal_year.year} T{self.quarter}"
