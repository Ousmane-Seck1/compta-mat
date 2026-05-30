from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


@register.filter
def fmt_qty(value) -> str:
    """Quantite sans decimales, avec espace pour les milliers: 1 234"""
    try:
        n = Decimal(str(value))
        rounded = int(n)
        return f"{rounded:,}".replace(",", "\u00a0")
    except (InvalidOperation, TypeError, ValueError):
        return str(value) if value is not None else ""


@register.filter
def fmt_amount(value) -> str:
    """Montant sans decimales, avec espace pour les milliers: 1 234 567"""
    return fmt_qty(value)


@register.filter
def blank_if_zero(value):
    """Retourne une chaine vide si la valeur est numeriquement egale a 0."""
    if value is None:
        return ""
    text = str(value).strip()
    if text == "":
        return ""
    try:
        normalized = text.replace("\xa0", "").replace(" ", "").replace(",", ".")
        return "" if Decimal(normalized) == Decimal("0") else value
    except (InvalidOperation, TypeError, ValueError):
        return value
