from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from .models import InternalMovement, Location, Material, NomenclatureItem, PhysicalInventory, Structure, StructureType, UserProfile, Voucher


User = get_user_model()


VOUCHER_TYPE_CHOICES = [
    (Voucher.TYPE_ENTRY, "Bon d'entree"),
    (Voucher.TYPE_FINAL_EXIT, "Bon de sortie definitive"),
    (Voucher.TYPE_TEMP_EXIT, "Bon de sortie provisoire"),
]

USER_MANAGED_ACCESS_SCOPE_CHOICES = [
    (UserProfile.ACCESS_SCOPE_SERVICE, "Un service donne uniquement"),
    (UserProfile.ACCESS_SCOPE_CATEGORY, "Tous les services d'une meme categorie"),
]


@dataclass(slots=True)
class VoucherLineInput:
    material_id: int
    specification: str
    quantity: Decimal
    unit_price: Decimal


@dataclass(slots=True)
class InternalMovementLineInput:
    material_id: int
    inventory_code: str
    quantity: Decimal
    unit_price: Decimal
    observations: str


class NomenclatureItemForm(ModelForm):
    def clean_account_code(self):
        account_code = (self.cleaned_data.get("account_code") or "").strip()
        if not account_code:
            return account_code
        duplicate_exists = NomenclatureItem.objects.filter(account_code__iexact=account_code).exists()
        if self.instance and self.instance.pk:
            duplicate_exists = NomenclatureItem.objects.filter(account_code__iexact=account_code).exclude(pk=self.instance.pk).exists()
        if duplicate_exists:
            raise forms.ValidationError("Ce code de compte existe deja dans la nomenclature.")
        return account_code

    class Meta:
        model = NomenclatureItem
        fields = ["account_code", "name", "unit", "group_code"]
        labels = {
            "account_code": "Compte",
            "name": "Intitule",
            "unit": "Unite",
            "group_code": "Code groupe",
        }


class MaterialForm(ModelForm):
    def __init__(self, *args, structure=None, fiscal_year=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.structure = structure
        self.fiscal_year = fiscal_year

    def clean_account_code(self):
        account_code = (self.cleaned_data.get("account_code") or "").strip()
        if not account_code:
            return account_code
        if self.structure and self.fiscal_year:
            duplicate_exists = Material.objects.filter(
                structure=self.structure,
                fiscal_year=self.fiscal_year,
                account_code__iexact=account_code,
            ).exists()
            if duplicate_exists:
                raise forms.ValidationError("Ce compte existe deja pour ce service et cet exercice.")
        return account_code

    class Meta:
        model = Material
        fields = ["account_code", "name", "unit", "group_code"]
        labels = {
            "account_code": "Compte",
            "name": "Intitule",
            "unit": "Unite",
            "group_code": "Code groupe",
        }


class PhysicalInventoryForm(ModelForm):
    pending_qty = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=0,
        max_digits=14,
        initial=0,
        label="Matieres en attente d'affectation",
        widget=forms.NumberInput(attrs={"step": "1", "min": "0"}),
    )
    in_service_qty = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=0,
        max_digits=14,
        initial=0,
        label="Matieres en service",
        widget=forms.NumberInput(attrs={"step": "1", "min": "0"}),
    )
    provisional_qty = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=0,
        max_digits=14,
        initial=0,
        label="Matieres en sortie provisoire",
        widget=forms.NumberInput(attrs={"step": "1", "min": "0"}),
    )

    def clean_pending_qty(self):
        return self.cleaned_data.get("pending_qty") or Decimal("0")

    def clean_in_service_qty(self):
        return self.cleaned_data.get("in_service_qty") or Decimal("0")

    def clean_provisional_qty(self):
        return self.cleaned_data.get("provisional_qty") or Decimal("0")

    class Meta:
        model = PhysicalInventory
        fields = ["pending_qty", "in_service_qty", "provisional_qty"]


class QuarterlyReportForm(forms.Form):
    QUARTER_CHOICES = [
        (1, "Trimestre 1"),
        (2, "Trimestre 2"),
        (3, "Trimestre 3"),
    ]
    quarter = forms.ChoiceField(label="Trimestre", choices=QUARTER_CHOICES)
    name = forms.CharField(label="Nom du rapport", max_length=120)


class LocationForm(ModelForm):
    pending_status = forms.BooleanField(
        required=False,
        label="En attente d'affectation (lieu de stockage / magasin)",
    )
    in_service_status = forms.BooleanField(
        required=False,
        label="En service (bureau, salle, parc auto, autre)",
    )
    store_type = forms.ChoiceField(
        required=False,
        label="Type de magasin",
        choices=[
            (Location.TYPE_STORE_EQUIPMENT, "Magasin principal (materiel et equipement)"),
            (Location.TYPE_STORE_SUPPLIES, "Magasin de fournitures"),
            (Location.TYPE_STORE_PRODUCTS, "Magasin de produits"),
        ],
    )
    service_type = forms.ChoiceField(
        required=False,
        label="Type de localisation en service",
        choices=[
            (Location.TYPE_OFFICE, "Bureau"),
            (Location.TYPE_ROOM, "Salle"),
            (Location.TYPE_VEHICLE_PARK, "Parc auto"),
            (Location.TYPE_OTHER, "Autre localisation"),
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            is_store = instance.is_store
            self.fields["pending_status"].initial = is_store
            self.fields["in_service_status"].initial = not is_store
            if is_store:
                self.fields["store_type"].initial = instance.location_type
                self.fields["service_type"].initial = Location.TYPE_OFFICE
            else:
                self.fields["service_type"].initial = instance.location_type
                self.fields["store_type"].initial = Location.TYPE_STORE_EQUIPMENT
        else:
            self.fields["pending_status"].initial = True
            self.fields["in_service_status"].initial = False
            self.fields["store_type"].initial = Location.TYPE_STORE_EQUIPMENT
            self.fields["service_type"].initial = Location.TYPE_OFFICE

    def clean(self):
        cleaned_data = super().clean()
        pending_status = bool(cleaned_data.get("pending_status"))
        in_service_status = bool(cleaned_data.get("in_service_status"))

        if pending_status == in_service_status:
            raise forms.ValidationError(
                "Cochez une seule option de statut: soit 'En attente d'affectation', soit 'En service'."
            )

        if pending_status:
            store_type = cleaned_data.get("store_type") or Location.TYPE_STORE_EQUIPMENT
            cleaned_data["location_type"] = store_type
        else:
            service_type = cleaned_data.get("service_type") or Location.TYPE_OFFICE
            cleaned_data["location_type"] = service_type
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.location_type = self.cleaned_data["location_type"]
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Location
        fields = ["name", "responsible_name", "details", "is_active"]
        labels = {
            "name": "Nom de la localisation",
            "responsible_name": "Responsable",
            "details": "Observations",
            "is_active": "Active",
        }


class InternalMovementHeaderForm(forms.Form):
    movement_type = forms.ChoiceField(label="Type de mouvement", choices=InternalMovement.TYPE_CHOICES)
    operation_date = forms.DateField(label="Date du mouvement", widget=forms.DateInput(attrs={"type": "date"}))
    from_location = forms.ModelChoiceField(label="Localisation source", queryset=Location.objects.none())
    to_location = forms.ModelChoiceField(label="Localisation destination", queryset=Location.objects.none())
    reason = forms.CharField(label="Motif", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, structure=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Location.objects.filter(is_active=True).order_by("name")
        if structure is not None:
            queryset = queryset.filter(structure=structure)
        self.fields["from_location"].queryset = queryset
        self.fields["to_location"].queryset = queryset


class ProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ["display_name", "default_structure", "assigned_structures"]


class UserCreationWithProfileForm(UserCreationForm):
    role = forms.ChoiceField(label="Role", choices=UserProfile.ROLE_CHOICES, initial=UserProfile.ROLE_VIEWER)
    access_scope = forms.ChoiceField(
        label="Portee d'acces",
        choices=USER_MANAGED_ACCESS_SCOPE_CHOICES,
        initial=UserProfile.ACCESS_SCOPE_SERVICE,
    )
    assigned_structure_type = forms.ModelChoiceField(
        label="Categorie de services",
        queryset=StructureType.objects.all().order_by("code"),
        required=False,
    )
    display_name = forms.CharField(label="Nom d'affichage", max_length=150, required=False)
    default_structure = forms.ModelChoiceField(
        label="Service par defaut",
        queryset=Structure.objects.filter(is_active=True).order_by("code"),
        required=False,
    )
    assigned_structures = forms.ModelMultipleChoiceField(
        label="Services autorises",
        queryset=Structure.objects.filter(is_active=True).order_by("code"),
        required=False,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        access_scope = cleaned_data.get("access_scope")
        assigned_structure_type = cleaned_data.get("assigned_structure_type")
        assigned_structures = cleaned_data.get("assigned_structures")
        default_structure = cleaned_data.get("default_structure")

        if access_scope == UserProfile.ACCESS_SCOPE_CATEGORY and not assigned_structure_type:
            raise forms.ValidationError("Selectionnez une categorie de services pour ce niveau d'acces.")

        if access_scope == UserProfile.ACCESS_SCOPE_SERVICE and not assigned_structures:
            raise forms.ValidationError("Selectionnez au moins un service pour cet utilisateur.")

        if access_scope == UserProfile.ACCESS_SCOPE_SERVICE and default_structure and default_structure not in assigned_structures:
            raise forms.ValidationError("Le service par defaut doit faire partie des services autorises.")

        if (
            access_scope == UserProfile.ACCESS_SCOPE_CATEGORY
            and assigned_structure_type
            and default_structure
            and default_structure.structure_type_id != assigned_structure_type.id
        ):
            raise forms.ValidationError("Le service par defaut doit appartenir a la categorie selectionnee.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data["role"]
        user.is_staff = role == UserProfile.ROLE_ADMIN

        if commit:
            user.save()
            profile = user.profile
            access_scope = self.cleaned_data.get("access_scope")
            assigned_structure_type = self.cleaned_data.get("assigned_structure_type")
            assigned_structures = self.cleaned_data.get("assigned_structures")
            default_structure = self.cleaned_data.get("default_structure")
            if access_scope == UserProfile.ACCESS_SCOPE_SERVICE and not default_structure and assigned_structures:
                default_structure = assigned_structures.first()
            if access_scope == UserProfile.ACCESS_SCOPE_CATEGORY and not default_structure and assigned_structure_type:
                default_structure = Structure.objects.filter(
                    is_active=True,
                    structure_type=assigned_structure_type,
                ).order_by("code").first()
            profile.role = role
            profile.access_scope = access_scope
            profile.assigned_structure_type = assigned_structure_type if access_scope == UserProfile.ACCESS_SCOPE_CATEGORY else None
            profile.display_name = self.cleaned_data.get("display_name", "")
            profile.default_structure = default_structure
            profile.save()
            if access_scope == UserProfile.ACCESS_SCOPE_SERVICE:
                profile.assigned_structures.set(assigned_structures)
            else:
                profile.assigned_structures.clear()

        return user


class UserUpdateWithProfileForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150)
    role = forms.ChoiceField(label="Role", choices=UserProfile.ROLE_CHOICES, initial=UserProfile.ROLE_VIEWER)
    access_scope = forms.ChoiceField(
        label="Portee d'acces",
        choices=USER_MANAGED_ACCESS_SCOPE_CHOICES,
        initial=UserProfile.ACCESS_SCOPE_SERVICE,
    )
    assigned_structure_type = forms.ModelChoiceField(
        label="Categorie de services",
        queryset=StructureType.objects.all().order_by("code"),
        required=False,
    )
    display_name = forms.CharField(label="Nom d'affichage", max_length=150, required=False)
    default_structure = forms.ModelChoiceField(
        label="Service par defaut",
        queryset=Structure.objects.filter(is_active=True).order_by("code"),
        required=False,
    )
    assigned_structures = forms.ModelMultipleChoiceField(
        label="Services autorises",
        queryset=Structure.objects.filter(is_active=True).order_by("code"),
        required=False,
    )
    is_active = forms.BooleanField(label="Compte actif", required=False, initial=True)

    def __init__(self, *args, user_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_instance = user_instance

        if user_instance and not self.is_bound:
            profile = getattr(user_instance, "profile", None)
            self.initial.update(
                {
                    "username": user_instance.username,
                    "role": getattr(profile, "role", UserProfile.ROLE_VIEWER),
                    "access_scope": getattr(profile, "access_scope", UserProfile.ACCESS_SCOPE_SERVICE),
                    "assigned_structure_type": getattr(profile, "assigned_structure_type", None),
                    "display_name": getattr(profile, "display_name", ""),
                    "default_structure": getattr(profile, "default_structure", None),
                    "assigned_structures": getattr(profile, "assigned_structures", Structure.objects.none()).all() if profile else Structure.objects.none(),
                    "is_active": user_instance.is_active,
                }
            )

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise forms.ValidationError("Le nom d'utilisateur est obligatoire.")
        qs = User.objects.filter(username__iexact=username)
        if self.user_instance is not None:
            qs = qs.exclude(pk=self.user_instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce nom d'utilisateur existe deja.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        access_scope = cleaned_data.get("access_scope")
        assigned_structure_type = cleaned_data.get("assigned_structure_type")
        assigned_structures = cleaned_data.get("assigned_structures")
        default_structure = cleaned_data.get("default_structure")

        if access_scope == UserProfile.ACCESS_SCOPE_CATEGORY and not assigned_structure_type:
            raise forms.ValidationError("Selectionnez une categorie de services pour ce niveau d'acces.")

        if access_scope == UserProfile.ACCESS_SCOPE_SERVICE and not assigned_structures:
            raise forms.ValidationError("Selectionnez au moins un service pour cet utilisateur.")

        if access_scope == UserProfile.ACCESS_SCOPE_SERVICE and default_structure and default_structure not in assigned_structures:
            raise forms.ValidationError("Le service par defaut doit faire partie des services autorises.")

        if (
            access_scope == UserProfile.ACCESS_SCOPE_CATEGORY
            and assigned_structure_type
            and default_structure
            and default_structure.structure_type_id != assigned_structure_type.id
        ):
            raise forms.ValidationError("Le service par defaut doit appartenir a la categorie selectionnee.")

        return cleaned_data

    def save(self):
        if self.user_instance is None:
            raise ValueError("Aucun utilisateur a modifier.")

        user = self.user_instance
        role = self.cleaned_data["role"]
        access_scope = self.cleaned_data["access_scope"]
        assigned_structure_type = self.cleaned_data.get("assigned_structure_type")
        assigned_structures = self.cleaned_data.get("assigned_structures")
        default_structure = self.cleaned_data.get("default_structure")

        if access_scope == UserProfile.ACCESS_SCOPE_SERVICE and not default_structure and assigned_structures:
            default_structure = assigned_structures.first()
        if access_scope == UserProfile.ACCESS_SCOPE_CATEGORY and not default_structure and assigned_structure_type:
            default_structure = Structure.objects.filter(
                is_active=True,
                structure_type=assigned_structure_type,
            ).order_by("code").first()
        user.username = self.cleaned_data["username"]
        user.is_staff = role == UserProfile.ROLE_ADMIN
        user.is_active = self.cleaned_data.get("is_active", True)
        user.save(update_fields=["username", "is_staff", "is_active"])

        profile = user.profile
        profile.role = role
        profile.access_scope = access_scope
        profile.assigned_structure_type = assigned_structure_type if access_scope == UserProfile.ACCESS_SCOPE_CATEGORY else None
        profile.display_name = self.cleaned_data.get("display_name", "")
        profile.default_structure = default_structure
        profile.save()
        if access_scope == UserProfile.ACCESS_SCOPE_SERVICE:
            profile.assigned_structures.set(assigned_structures)
        else:
            profile.assigned_structures.clear()
        return user


class VoucherHeaderForm(forms.Form):
    voucher_type = forms.ChoiceField(label="Type de bon", choices=VOUCHER_TYPE_CHOICES)
    operation_date = forms.DateField(label="Date de l'operation", widget=forms.DateInput(attrs={"type": "date"}))
    source_or_destination = forms.CharField(
        label="Origine des entrées ou destination des sorties",
        max_length=255,
        required=False,
    )
    comments = forms.CharField(label="Commentaires", required=False, widget=forms.Textarea(attrs={"rows": 3}))


def parse_voucher_lines(post_data, *, max_lines: int = 8) -> list[VoucherLineInput]:
    try:
        max_lines = int(post_data.get("line_count") or max_lines)
    except (ValueError, TypeError):
        pass
    lines: list[VoucherLineInput] = []
    for index in range(max_lines):
        material_id = (post_data.get(f"line_material_{index}") or "").strip()
        specification = (post_data.get(f"line_specification_{index}") or "").strip()
        quantity = (post_data.get(f"line_quantity_{index}") or "").strip()
        unit_price = (post_data.get(f"line_unit_price_{index}") or "").strip()
        if not material_id and not quantity and not unit_price:
            continue
        if not material_id:
            raise forms.ValidationError(f"La ligne {index + 1} doit contenir une matiere.")
        try:
            quantity_value = Decimal(quantity)
        except Exception as error:  # noqa: BLE001
            raise forms.ValidationError(f"Quantite invalide a la ligne {index + 1}.") from error
        try:
            unit_price_value = Decimal(unit_price)
        except Exception as error:  # noqa: BLE001
            raise forms.ValidationError(f"Prix unitaire invalide a la ligne {index + 1}.") from error
        if quantity_value <= 0:
            raise forms.ValidationError(f"La quantite de la ligne {index + 1} doit etre positive.")
        if unit_price_value < 0:
            raise forms.ValidationError(f"Le prix unitaire de la ligne {index + 1} ne peut pas etre negatif.")
        lines.append(
            VoucherLineInput(
                material_id=int(material_id),
                specification=specification,
                quantity=quantity_value,
                unit_price=unit_price_value,
            )
        )
    if not lines:
        raise forms.ValidationError("Le bon doit contenir au moins une ligne.")
    return lines


def parse_internal_movement_lines(post_data, *, max_lines: int = 8) -> list[InternalMovementLineInput]:
    try:
        max_lines = int(post_data.get("line_count") or max_lines)
    except (ValueError, TypeError):
        pass
    lines: list[InternalMovementLineInput] = []
    for index in range(max_lines):
        material_id = (post_data.get(f"line_material_{index}") or "").strip()
        inventory_code = (post_data.get(f"line_inventory_code_{index}") or "").strip()
        quantity = (post_data.get(f"line_quantity_{index}") or "").strip()
        unit_price = (post_data.get(f"line_unit_price_{index}") or "").strip()
        observations = (post_data.get(f"line_observations_{index}") or "").strip()
        if not material_id and not quantity and not unit_price and not inventory_code and not observations:
            continue
        if not material_id:
            raise forms.ValidationError(f"La ligne {index + 1} doit contenir une matiere.")
        try:
            quantity_value = Decimal(quantity)
        except Exception as error:  # noqa: BLE001
            raise forms.ValidationError(f"Quantite invalide a la ligne {index + 1}.") from error
        try:
            unit_price_value = Decimal(unit_price)
        except Exception as error:  # noqa: BLE001
            raise forms.ValidationError(f"Prix unitaire invalide a la ligne {index + 1}.") from error
        if quantity_value <= 0:
            raise forms.ValidationError(f"La quantite de la ligne {index + 1} doit etre positive.")
        if unit_price_value < 0:
            raise forms.ValidationError(f"Le prix unitaire de la ligne {index + 1} ne peut pas etre negatif.")
        lines.append(
            InternalMovementLineInput(
                material_id=int(material_id),
                inventory_code=inventory_code,
                quantity=quantity_value,
                unit_price=unit_price_value,
                observations=observations,
            )
        )
    if not lines:
        raise forms.ValidationError("Le bordereau doit contenir au moins une ligne.")
    return lines
