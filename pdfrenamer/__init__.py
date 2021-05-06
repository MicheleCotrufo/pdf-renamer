import logging

# Setup logging
logger = logging.getLogger("pdf-renamer")
logger.setLevel(level=logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("[pdf-renamer] %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
logger.propagate = False

from .pdfrenamer import rename,build_filename

