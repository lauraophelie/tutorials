from dataclasses import dataclass
from pathlib import Path 

@dataclass(frozen=True)
class ImportConfig:
    # configuration de l'import
    odoo_config: Path
    excel_file: Path
    sheet_name: str = "Properties"
    dry_run: bool = False
    log_dir: Path = Path(__file__).parent.parent / "logs"

    def __post__init(self):
        if not self.odoo_config.exists():
            raise FileNotFoundError(f"odoo.conf introuvable : {self.odoo_config}")
        if not self.excel_file.exists():
            raise FileNotFoundError(f"Fichier Excel introuvable : {self.excel_file}")