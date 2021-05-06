import logging

## Setup logging
#logger = logging.getLogger("pdf_renamer")
#logger.setLevel(level=logging.INFO)
#if not logger.handlers:
#    formatter = logging.Formatter("[pdf_renamer] %(message)s")
#    ch = logging.StreamHandler()
#    ch.setFormatter(formatter)
#    logger.addHandler(ch)
#logger.propagate = False

from .pdf_renamer import rename,build_filename

