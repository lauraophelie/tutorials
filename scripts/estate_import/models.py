from dataclasses import dataclass, field

@dataclass
class PropertyTypeDTO:
    """Représente un type de propriété extrait du fichier Excel."""
    name: str

@dataclass
class PropertyTagDTO:
    """Représente un tag extrait du fichier Excel."""
    name: str

@dataclass
class PropertyOfferDTO:
    """Représente une offre liée à une propriété."""
    partner_name: str
    price: float
    validity: int = 7

@dataclass
class PropertyDTO:
    """
    Représente une propriété extraite du fichier Excel.

    Les champs optionnels ont des valeurs par défaut sensées.
    """
    name: str
    property_type: PropertyTypeDTO | None = None
    tags: list[PropertyTagDTO] = field(default_factory=list)
    offers: list[PropertyOfferDTO] = field(default_factory=list)
    postcode: str | None = None
    expected_price: float = 0.0
    bedrooms: int = 2
    living_area: int = 0
    garden: bool = False
    garden_area: int = 0
    garden_orientation: str | None = None