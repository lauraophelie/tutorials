"""
REPL interactif pour Odoo.

Usage :
    python scripts/repl.py --config odoo.conf

Une fois lancé, vous avez accès à :
    env         → l'environnement Odoo (accès à tous les modèles)
    db          → le nom de la base
    odoo        → le module odoo lui-même

Exemples dans le REPL :
    >>> env["estate.property"].search([])
    >>> env["estate.property"].search_count([])
    >>> env["estate.property"].create({"name": "Test", "expected_price": 100000})
    >>> env.cr.commit()  # pour valider
    >>> env.cr.rollback()  # pour annuler
"""

import argparse
import code
import sys
from pathlib import Path

# Ajoute la racine Odoo au PYTHONPATH
ODOO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ODOO_ROOT))

import odoo
from odoo.api import Environment

def main():
    parser = argparse.ArgumentParser(description="REPL interactif Odoo")
    parser.add_argument("--config", required=True, type=Path, help="Chemin vers odoo.conf")
    args = parser.parse_args()

    # Charge la config Odoo
    odoo.tools.config.parse_config(["-c", str(args.config)])
    db_name = odoo.tools.config["db_name"]

    if not db_name:
        print("Erreur : db_name non configuré dans odoo.conf")
        sys.exit(1)

    print(f"Connexion à la base '{db_name}'...")
    registry = odoo.registry(db_name)
    cr = registry.cursor()
    env = Environment(cr, odoo.SUPERUSER_ID, {})

    print()
    print("=" * 60)
    print("REPL Odoo — tapez du Python, 'exit()' pour quitter")
    print("=" * 60)
    print()
    print("Variables disponibles :")
    print("  env      → Environment Odoo")
    print("  db       → nom de la base")
    print("  odoo     → module odoo")
    print()
    print("Rappels :")
    print("  env.cr.commit()    → valider les modifications")
    print("  env.cr.rollback()  → annuler les modifications")
    print()

    # Contexte du REPL
    namespace = {
        "env": env,
        "db": db_name,
        "odoo": odoo,
    }

    try:
        code.interact(local=namespace, banner="")
    finally:
        # Demande à l'utilisateur s'il veut commit ou rollback
        print()
        choice = input("Commit (c) / Rollback (r) / Rien (n) ? [n] ").strip().lower()
        if choice == "c":
            cr.commit()
            print("Transaction commitée.")
        elif choice == "r":
            cr.rollback()
            print("Transaction annulée.")
        else:
            cr.rollback()
            print("Rien n'a été modifié.")
        cr.close()


if __name__ == "__main__":
    main()