import logging
from datetime import datetime
from pathlib import Path


def setup_logger(name: str, log_dir: Path) -> logging.Logger:
    """
    Crée un logger qui écrit à la fois sur la console et dans un fichier.

    Le fichier est horodaté pour conserver l'historique des imports.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{name}_{datetime.now():%Y-%m-%d_%H-%M-%S}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(ch)

    logger.info(f"Log file: {log_file}")
    return logger