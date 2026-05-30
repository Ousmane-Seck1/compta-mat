from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from .models import FiscalYear, Structure, UserProfile


class StructureMiddleware:
    """Middleware pour gérer la structure et l'exercice courants dans la session."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            profile = getattr(request.user, "profile", None)
            if profile is None:
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
            
            # Déterminer la structure courante
            if profile:
                # Admin voit tous les services
                if profile.role == "admin":
                    structure_id = request.session.get("structure_id")
                    if not structure_id:
                        # Utiliser la première structure disponible
                        try:
                            structure = Structure.objects.filter(is_active=True).first()
                            if structure:
                                request.session["structure_id"] = structure.id
                        except Structure.DoesNotExist:
                            pass
                else:
                    current_structure_id = request.session.get("structure_id")
                    is_current_allowed = bool(
                        current_structure_id
                        and profile.assigned_structures.filter(id=current_structure_id, is_active=True).exists()
                    )

                    # Non-admin: conserver le service choisi s'il est autorisé, sinon appliquer un fallback.
                    if not is_current_allowed:
                        if profile.default_structure and profile.default_structure.is_active and profile.assigned_structures.filter(id=profile.default_structure.id, is_active=True).exists():
                            request.session["structure_id"] = profile.default_structure.id
                        else:
                            assigned_active = profile.assigned_structures.filter(is_active=True).order_by("code").first()
                            if assigned_active:
                                request.session["structure_id"] = assigned_active.id
            
            # Déterminer l'exercice courant
            structure_id = request.session.get("structure_id")
            if structure_id:
                try:
                    structure = Structure.objects.get(id=structure_id)
                    fiscal_year_id = request.session.get("fiscal_year_id")

                    # Valider que l'exercice en session appartient bien a la structure courante.
                    if fiscal_year_id and not FiscalYear.objects.filter(id=fiscal_year_id, structure=structure).exists():
                        fiscal_year_id = None
                        request.session.pop("fiscal_year_id", None)

                    if not fiscal_year_id:
                        # Priorite: exercice 2025 si disponible, sinon exercice actif, sinon le plus recent.
                        fy = FiscalYear.objects.filter(structure=structure, year=2025).first()
                        if not fy:
                            fy = FiscalYear.objects.filter(
                                structure=structure,
                                is_active=True,
                                is_closed=False,
                            ).order_by("-year").first()
                        if not fy:
                            fy = FiscalYear.objects.filter(structure=structure).order_by("-year").first()
                        if fy:
                            request.session["fiscal_year_id"] = fy.id
                except Structure.DoesNotExist:
                    pass
            
            # Ajouter les données au context
            structure_id = request.session.get("structure_id")
            fiscal_year_id = request.session.get("fiscal_year_id")
            
            try:
                if structure_id:
                    request.current_structure = Structure.objects.get(id=structure_id)
                else:
                    request.current_structure = None
                    
                if fiscal_year_id:
                    request.current_fiscal_year = FiscalYear.objects.get(id=fiscal_year_id)
                else:
                    request.current_fiscal_year = None
            except (Structure.DoesNotExist, FiscalYear.DoesNotExist):
                request.current_structure = None
                request.current_fiscal_year = None
        else:
            request.current_structure = None
            request.current_fiscal_year = None

        response = self.get_response(request)
        return response
