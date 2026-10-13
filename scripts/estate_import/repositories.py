"""
Repositories — accès à l'ORM Odoo.

Principe SOLID (S) : une seule responsabilité — parler à Odoo.
Principe SOLID (D) : les services dépendent de ces repositories, pas d'Odoo directement.

Chaque repository encapsule les opérations CRUD pour un modèle Odoo.
"""

from odoo.api import Environment

from .models import PropertyDTO, PropertyTypeDTO, PropertyTagDTO, PropertyOfferDTO


class BaseRepository:
    """Repository de base avec les opérations communes."""

    def __init__(self, env: Environment, dry_run: bool = False):
        self.env = env
        self.dry_run = dry_run

    def _get_or_create(self, model_name: str, domain: list, values: dict):
        """
        Récupère un enregistrement existant ou le crée.

        Retourne (record, created).
        En mode dry-run, retourne un record vide sans écrire.
        """
        model = self.env[model_name]
        record = model.search(domain, limit=1)
        if record:
            return record, False

        if self.dry_run:
            # En dry-run, on ne peut pas créer — on retourne un record vide
            return model.browse(), True

        record = model.create(values)
        return record, True


class PropertyTypeRepository(BaseRepository):
    """Repository pour estate.property.type."""

    MODEL = "estate.property.type"

    def get_or_create(self, dto: PropertyTypeDTO):
        """Récupère ou crée un type de propriété."""
        return self._get_or_create(
            self.MODEL,
            [("name", "=", dto.name)],
            {"name": dto.name},
        )


class PropertyTagRepository(BaseRepository):
    """Repository pour estate.property.tag."""

    MODEL = "estate.property.tag"

    def get_or_create(self, dto: PropertyTagDTO):
        """Récupère ou crée un tag."""
        return self._get_or_create(
            self.MODEL,
            [("name", "=", dto.name)],
            {"name": dto.name},
        )


class PartnerRepository(BaseRepository):
    """Repository pour res.partner."""

    MODEL = "res.partner"

    def get_or_create(self, name: str):
        """Récupère ou crée un partenaire par nom."""
        return self._get_or_create(
            self.MODEL,
            [("name", "=", name)],
            {"name": name},
        )


class PropertyRepository(BaseRepository):
    """Repository pour estate.property."""

    MODEL = "estate_property"

    def find_by_name(self, name: str):
        """Retourne la propriété avec ce nom, ou un record vide."""
        return self.env[self.MODEL].search([("name", "=", name)], limit=1)

    def create(self, dto: PropertyDTO, type_id: int | None, tag_ids: list[int]):
        """
        Crée une propriété à partir d'un DTO.

        En dry-run, ne fait rien et retourne un record vide.
        """
        if self.dry_run:
            return self.env[self.MODEL].browse()

        vals = {
            "name": dto.name,
            "property_type_id": type_id or False,
            "tag_ids": [(6, 0, tag_ids)],
            "postcode": dto.postcode,
            "expected_price": dto.expected_price,
            "bedrooms": dto.bedrooms,
            "living_area": dto.living_area,
            "garden": dto.garden,
            "garden_area": dto.garden_area,
            "garden_orientation": dto.garden_orientation,
        }
        return self.env[self.MODEL].create(vals)


class OfferRepository(BaseRepository):
    """Repository pour estate.property.offer."""

    MODEL = "estate.property.offer"

    def create(self, dto: PropertyOfferDTO, property_id: int, partner_id: int):
        """Crée une offre liée à une propriété et un partenaire."""
        if self.dry_run:
            return self.env[self.MODEL].browse()

        return self.env[self.MODEL].create({
            "price": dto.price,
            "validity": dto.validity,
            "partner_id": partner_id,
            "property_id": property_id,
        })