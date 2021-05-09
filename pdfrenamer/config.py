import platform
system = platform.system()

if system.lower() == ('windows'): 
    separator = '\\'
else: 
    separator = '/'

# Setup logging
import logging
logger = logging.getLogger("pdf-renamer")
logger.setLevel(level=logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter("[pdf-renamer] %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
logger.propagate = False

#Parameters for this library
format = "{YYYY}-{MM} - {J} - {A3etal} - {T}" #Default value for the filename format, which will be used if no format is specified by user
additional_abbreviations_file = None #Global variable, it stores the path of a potential additional file with journal abbreviations
max_length_authors = 80 #Maximum length of any string related to authors
max_length_filename = 250 #Maximum filename length

#Parameters for the pdf2doi library
check_online_to_validate = True
websearch = True
numb_results_google_search = 6 #How many results should it look into when doing a google search