import logging

# Setup logging
logger = logging.getLogger("pdf-renamer")
logger.setLevel(level=logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("[pdf-renamer]: %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
logger.propagate = False

from .config import config
config.ReadParamsINIfile()

config.set('verbose',config.get('verbose')) #This is a quick and dirty way (to improve in the future) to make sure that the verbosity of the pdf2doi logger is properly set according
                                            #to the current value of config.get('verbose') (see config.py file for details)

from .main import rename,build_filename
from .filename_creators import *

