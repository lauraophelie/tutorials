"""
Interface ligne de commande.

Principe SOLID (S) : une seule responsabilité — parser les arguments et orchestrer.
"""

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Import de propriétés immobilières dans Odoo depuis Excel.",
    )
    parser.add_argument(
        "--config", required=True, type=Path,
        help="Chemin vers odoo.conf",
    )
    parser.add_argument(
        "--file", required=True, type=Path,
        help="Chemin vers le fichier Excel",
    )
    parser.add_argument(
        "--sheet", default="Properties",
        help="Nom de la feuille Excel (défaut : Properties)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simule l'import sans écrire en base",
    )
    return parser.parse_args()