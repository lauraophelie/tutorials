"""
Point d'entrée principal.

Usage :
    python -m estate_import --config odoo.conf --file data/properties.xlsx [--dry-run]
"""

import sys
from pathlib import Path

# Ajoute la racine Odoo au PYTHONPATH pour importer odoo
ODOO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ODOO_ROOT))

import odoo
from odoo.api import Environment

from .cli import parse_args
from .config import ImportConfig
from .logger import setup_logger
from .readers import ExcelPropertyReader
from .validators import validate_property, ValidationError
from .services import PropertyImportService


def main():
    args = parse_args()

    # 1. Configuration
    try:
        config = ImportConfig(
            odoo_config=args.config,
            excel_file=args.file,
            sheet_name=args.sheet,
            dry_run=args.dry_run,
        )
    except FileNotFoundError as e:
        print(f"Erreur de configuration : {e}")
        sys.exit(1)

    # 2. Logging
    logger = setup_logger("estate_import", config.log_dir)
    logger.info(f"Démarrage de l'import (dry_run={config.dry_run})")
    logger.info(f"Fichier Excel : {config.excel_file}")

    # 3. Lecture du fichier
    try:
        reader = ExcelPropertyReader(config.excel_file, config.sheet_name)
        properties = reader.read()
        logger.info(f"{len(properties)} propriétés lues")
    except Exception as e:
        logger.error(f"Erreur de lecture : {e}", exc_info=True)
        sys.exit(1)

    # 4. Validation
    valid_properties = []
    for prop in properties:
        try:
            validate_property(prop)
            valid_properties.append(prop)
        except ValidationError as e:
            logger.error(f"Validation échouée pour '{prop.name}' : {e}")

    logger.info(f"{len(valid_properties)} propriétés valides sur {len(properties)}")

    # 5. Connexion Odoo
    odoo.tools.config.parse_config(["-c", str(config.odoo_config)])
    db_name = odoo.tools.config["db_name"]
    if not db_name:
        logger.error("db_name non configuré dans odoo.conf")
        sys.exit(1)

    logger.info(f"Connexion à la base '{db_name}'...")

    registry = odoo.registry(db_name)
    with registry.cursor() as cr:
        env = Environment(cr, odoo.SUPERUSER_ID, {})
        try:
            # 6. Import
            service = PropertyImportService(env, logger, dry_run=config.dry_run)
            stats = service.import_all(valid_properties)

            # 7. Commit ou rollback
            if config.dry_run:
                logger.info("Mode dry-run : rollback")
                cr.rollback()
            else:
                cr.commit()
                logger.info("Transaction commitée")

            # 8. Rapport final
            logger.info("=" * 50)
            logger.info("RAPPORT D'IMPORT")
            logger.info("=" * 50)
            logger.info(f"Propriétés créées : {stats['properties_created']}")
            logger.info(f"Types créés      : {stats['types_created']}")
            logger.info(f"Tags créés       : {stats['tags_created']}")
            logger.info(f"Offres créées    : {stats['offers_created']}")
            logger.info(f"Erreurs          : {stats['errors']}")

        except Exception as e:
            cr.rollback()
            logger.error(f"Erreur fatale, rollback : {e}", exc_info=True)
            sys.exit(1)


if __name__ == "__main__":
    main()