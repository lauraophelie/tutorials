"""
Services métier — orchestration.

Principe SOLID (S) : une seule responsabilité — orchestrer l'import.
Principe SOLID (D) : dépend des repositories, pas d'Odoo directement.

C'est ici que vit la logique métier : « comment importer une propriété
avec ses types, tags et offres ».
"""

import logging

from odoo.api import Environment

from .models import PropertyDTO
from .repositories import (
    PropertyTypeRepository,
    PropertyTagRepository,
    PartnerRepository,
    PropertyRepository,
    OfferRepository,
)


class PropertyImportService:
    """
    Service d'import de propriétés.

    Orchestre la création des types, tags, partenaires, propriétés et offres.
    """

    def __init__(self, env: Environment, logger: logging.Logger, dry_run: bool = False):
        self.env = env
        self.logger = logger
        self.dry_run = dry_run

        # Instanciation des repositories (injection de dépendances)
        self.types = PropertyTypeRepository(env, dry_run)
        self.tags = PropertyTagRepository(env, dry_run)
        self.partners = PartnerRepository(env, dry_run)
        self.properties = PropertyRepository(env, dry_run)
        self.offers = OfferRepository(env, dry_run)

    def import_property(self, dto: PropertyDTO) -> dict:
        """
        Importe une propriété complète (type, tags, offres).

        Retourne un dict de statistiques :
        {
            "property_created": bool,
            "type_created": bool,
            "tags_created": int,
            "offers_created": int,
        }
        """
        stats = {
            "property_created": False,
            "type_created": False,
            "tags_created": 0,
            "offers_created": 0,
        }

        # 1. Vérifier les doublons
        existing = self.properties.find_by_name(dto.name)
        if existing:
            self.logger.warning(
                f"Propriété '{dto.name}' existe déjà (id={existing.id}), ignorée"
            )
            return stats

        # 2. Résoudre ou créer le type
        type_id = None
        if dto.property_type:
            type_rec, created = self.types.get_or_create(dto.property_type)
            type_id = type_rec.id
            if created:
                stats["type_created"] = True
                self.logger.info(f"Type créé : {dto.property_type.name}")

        # 3. Résoudre ou créer les tags
        tag_ids = []
        for tag_dto in dto.tags:
            tag_rec, created = self.tags.get_or_create(tag_dto)
            tag_ids.append(tag_rec.id)
            if created:
                stats["tags_created"] += 1
                self.logger.info(f"Tag créé : {tag_dto.name}")

        # 4. Créer la propriété
        prop = self.properties.create(dto, type_id, tag_ids)
        if not self.dry_run:
            stats["property_created"] = True
            self.logger.info(f"Propriété créée : {dto.name} (id={prop.id})")

        # 5. Créer les offres
        for offer_dto in dto.offers:
            partner_rec, _ = self.partners.get_or_create(offer_dto.partner_name)
            self.offers.create(offer_dto, prop.id, partner_rec.id)
            if not self.dry_run:
                stats["offers_created"] += 1
                self.logger.info(
                    f"Offre créée : {offer_dto.partner_name} "
                    f"({offer_dto.price} €) pour {dto.name}"
                )

        return stats

    def import_all(self, properties: list[PropertyDTO]) -> dict:
        """
        Importe toutes les propriétés et retourne les statistiques globales.
        """
        total = {
            "properties_created": 0,
            "types_created": 0,
            "tags_created": 0,
            "offers_created": 0,
            "errors": 0,
        }

        for prop_dto in properties:
            try:
                stats = self.import_property(prop_dto)
                if stats["property_created"]:
                    total["properties_created"] += 1
                if stats["type_created"]:
                    total["types_created"] += 1
                total["tags_created"] += stats["tags_created"]
                total["offers_created"] += stats["offers_created"]
            except Exception as e:
                total["errors"] += 1
                self.logger.error(
                    f"Erreur sur '{prop_dto.name}' : {e}", exc_info=True
                )

        return total