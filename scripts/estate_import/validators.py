"""
Validateurs de données.

Principe SOLID (S) : une seule responsabilité — valider.
Principe SOLID (O) : on peut ajouter des validateurs sans modifier les existants.

Chaque validateur est une fonction pure : pas d'effet de bord, facile à tester.
"""

from .models import PropertyDTO


class ValidationError(Exception):
    """Erreur de validation métier."""
    pass


def validate_property(prop: PropertyDTO) -> None:
    """
    Valide une propriété avant import.

    Lève ValidationError si une règle métier est violée.
    """
    if not prop.name or not prop.name.strip():
        raise ValidationError("Le nom de la propriété est obligatoire")

    if prop.expected_price < 0:
        raise ValidationError(
            f"Le prix attendu doit être positif (reçu : {prop.expected_price})"
        )

    if prop.bedrooms < 0:
        raise ValidationError(
            f"Le nombre de chambres doit être positif (reçu : {prop.bedrooms})"
        )

    if prop.garden and prop.garden_area < 0:
        raise ValidationError("La surface du jardin doit être positive")

    if prop.garden_orientation and prop.garden_orientation not in (
        "north", "south", "east", "west"
    ):
        raise ValidationError(
            f"Orientation invalide : {prop.garden_orientation}. "
            "Valeurs acceptées : north, south, east, west"
        )

    for offer in prop.offers:
        if offer.price <= 0:
            raise ValidationError(
                f"Le prix de l'offre doit être strictement positif (reçu : {offer.price})"
            )
        if offer.validity <= 0:
            raise ValidationError(
                f"La validité doit être positive (reçu : {offer.validity})"
            )