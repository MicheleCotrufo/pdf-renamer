import logging

# Setup logging

#Change the formatter for the logger of the pdf2doi library; add a prefix '\t' in front of all
#output created by pdf2doi
logger = logging.getLogger("pdf2doi")
logger.setLevel(level=logging.INFO)
logger.handlers =[]
if not logger.handlers:
    formatter = logging.Formatter("\t[pdf2doi]: %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
logger.propagate = False
#####

logger = logging.getLogger("pdf-renamer")
logger.setLevel(level=logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("[pdf-renamer] %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
logger.propagate = False

from .config import Config
from .main import rename,build_filename
from .filename_creators import *

