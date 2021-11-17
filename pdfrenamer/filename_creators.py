''' 
This module contains several functions and variables that are used to generate
a valid filename, based on the chosen format and the available infos
'''

import re
import pkgutil
import pdf2bib
import pdfrenamer.config as config
import logging
import unidecode
logger = logging.getLogger("pdf_renamer")

AllowedTags = {"{YYYY}":" \t\t=\t Year of publication",
                "{MM}":" \t\t=\t Month of publication (in digits)",
                "{DD}":" \t\t=\t Day of publication (in digits)",
                "{J}":" \t\t=\t Full name of Journal",
                "{Jabbr}":" \t=\t Abbreviated name of Journal, if any available (otherwise full name is used).",
                "{Aall}":" \t\t=\t Last name of all authors (separated by comma)",
                "{Aetal}":" \t=\t Last name of the first author, add \'et al.\' if more authors are present",
                "{A3etal}":" \t=\t Last name of the first three authors (separated by comma), add \'et al.\' if more authors are present",
                "{aAall}":" \t=\t First initial and last name of all authors (separated by comma)",
                "{aAetal}":" \t=\t First initial and last name of the first author, add \'et al.\' if more authors are present",
                "{aA3etal}":" \t=\t First initial and last name of the first three authors (separated by comma), add \'et al.\' if more authors are present",
                "{T}":" \t\t=\t Title."}

valid_months = {'jan':'01','january':'01',
                'feb':'02','february':'02',
                'mar':'03','march':'03',
                'apr':'04','april':'04',
                'may':'05','may':'05',
                'jun':'06','june':'06',
                'jul':'07','july':'07',
                'aug':'08','august':'08',
                'sep':'09','september':'09',
                'oct':'10','october':'10',
                'nov':'11','november':'11',
                'dec':'12','december':'12'}

def month_to_number(month_string):
    return valid_months.get(month_string,"00")

def validate_journal(journal):
    return journal

def is_valid_integer(string,number_digits):
    if not isinstance(string,str):
        string = str(string)
    return (string.isnumeric() and len(string)==number_digits)

def sanitize(string):
    #Given a string in input, it first removes all possible latex codes, and then removes any residual character which would not be 
    #allowed in a file name

    #Step 1. Replace common latex symbols
    replace ={       
                '-'  : ['{\\textendash}','{\\textemdash}'] ,
                '_'  : ['{\\textunderscore}'],
                ' '  : ["{\\textasteriskcentered}","{\\textgreater}","{\\textless}"],
                ''  : ["\n"],
                '{'  : ["{\\textbraceleft}"],
                '}'  : ["{\\textbraceright}"],
                "\'" : ["{\\textquotesingle}","{\\textquotedblleft}","{\\textquotedblright}","{\\textquoteleft}","{\\textquoteright}"]
                }
    for i, j in replace.items():
        for k in j:
            string = string.replace(k, i)
    string = re.sub(r"{\\hspace{.*}}", "",string)

    #Step 2. Find all substrings in the format {\string1{string2}} and replace them by string2
    #We use the function remove_latex_codes defined in the pdf2bib package
    string = pdf2bib.remove_latex_codes(string)

    #Step 3. Remove any residual special character
    invalid = "<>\"/\|*{}'?:"
    for char in invalid:
        string = string.replace(char, '')
    #Step 4. #Make a final check that the string is only made out of ascii characters (i.e. no accents, tildes, etc.)
    string = unidecode.unidecode(string) 

    #Step 5. If there are multiple spaces, replace them with only one
    string = re.sub(' +',' ',string)

    return string

def find_abbreviation_journal(journal_name):
    """
    Find a journal abbreviation for a given journal name.

    Parameters
    ----------
    journal_name : string
        Name of the Journal.

    Returns
    -------
    string
        The abbreviation of the journal if any is found, or None if no abbraviation is found

    """
    to_search = sanitize( (journal_name.strip() + " = ").lower() )

    data = pkgutil.get_data(__name__, "UserDefinedAbbreviations.txt").decode('utf8')
    for line in data.splitlines():
        if (line.lower()).startswith(to_search):
            return line[len(to_search):].rstrip()

    data = pkgutil.get_data(__name__, "StandardAbbreviations.txt").decode('utf8')
    for line in data.splitlines():
        if (line.lower()).startswith(to_search):
            return line[len(to_search):].rstrip()
    return None

def find_tags_in_format(format):
    #Given the input string 'format', it creates a list of all the tags "{str}" 
    #contained in it, by looking for stuff wrapped between { and }
    # Example, tags = ['{YYYY}', '{MM}', '{J}', '{A}', '{T}']
    tags = re.findall(r'\{.*?\}', format)       
    return tags

def check_format_is_valid(format):
    #Check if the input string 'format' is a valid format for a filename
    #Returns None if it is not a valid format, or a list of the tags contained in format otherwise
    if not format or (not isinstance(format,str)):
        logger.error(f"The specified format is not a valid string.")
        return None
    tags = find_tags_in_format(format)
    if not tags:
        logger.error(f"The specified format does not contain any tag. Tags must be delimited by {{ and }}.")
        return None
    for tag in tags:
        if not tag in AllowedTags:
            logger.error(f"The specified format contains \"{{{tag}}}\", which is not a valid tag.")
            logger.error(f"The valid tags are: " + ",".join(AllowedTags))
            return None
    return tags


def build_filename(infos,   format = None, tags=None):
    '''
    It generates a filename based on the metadata contained in the input dictionary 'infos', using the format specified 
    in the input string 'format'. The tags contained in format have been already identified, and passed to this function 
    in the input dictionary 'tags'. 
    '''
    if not format: format = config.get('format')
    rep_dict =  dict.fromkeys(tags) #Initialize a dictionary with keys equal to the elements of the list tags, and all the values set to None

    for key in infos.keys():
        infos[key] = str(infos[key])

    #Now we look in the keys of the 'rep_dict' dictionary and populate the values of the dictionary
    #by using the information contained in the 'infos' dictionary
   
    if '{YYYY}' in rep_dict.keys():
        rep_dict['{YYYY}'] = infos['year'] if ('year' in infos and is_valid_integer(infos['year'],4)) else '0000'

    if '{MM}'in rep_dict.keys():
        rep_dict['{MM}'] = '00'
        if ('month' in infos):
            if is_valid_integer(infos['month'],2):
                rep_dict['{MM}'] = infos['month']
            elif is_valid_integer(infos['month'],1):
                rep_dict['{MM}'] = '0'+infos['month']
            elif (infos['month'].lower() in valid_months.keys()):
                rep_dict['{MM}'] = month_to_number(infos['month'].lower())

    if '{DD}'in rep_dict.keys():
        rep_dict['{DD}'] = '00'
        if ('day' in infos):
            if is_valid_integer(infos['day'],2):
                rep_dict['{DD}'] = infos['day']
            elif is_valid_integer(infos['day'],1):
                rep_dict['{DD}'] = '0'+infos['day']

    if ('{J}' in rep_dict.keys()) or ('{Jabbr}' in rep_dict.keys()):
        if ('journal' in infos) and infos['journal']:
            rep_dict['{J}'] = validate_journal(infos['journal'])
            Jabbr = find_abbreviation_journal(infos['journal'])
            if Jabbr:
                rep_dict['{Jabbr}'] = Jabbr
            else:
                rep_dict['{Jabbr}'] = rep_dict['{J}']
        elif ('ejournal' in infos) and infos['ejournal']:
            rep_dict['{J}'] = infos['ejournal']
            rep_dict['{Jabbr}'] = infos['ejournal']
        else:
            rep_dict['{J}'] = '[NoJournal]'
            rep_dict['{Jabbr}'] = '[NoJourn]'

    author_info = ''
    if 'author' in infos.keys():
        author_info = infos['author']
    if 'authors' in infos.keys() and len(infos['authors'])>len(author_info):
        author_info = infos['authors']

    ListAuthorTags = ['{Aall}','{A3etal}','{Aetal}','{aAall}','{aA3etal}','{aAetal}']
    if any(item in rep_dict.keys() for item in ListAuthorTags):
        if author_info:
            #IMPORTANT: Here it is assumed that the string containing the authors names is in the format "firstname1, secondname1 ...  lastname1 and firstname2, secondname2 ...  lastname2 etc."
            authors = [author.strip() for author in author_info.split(" and ")]
            lastnames = [name.split()[-1] for name in authors]
            firstnames = [name.split()[:-1] if len(name.split())>1 else [''] for name in authors]   #   The check on len(name.split())>1 is necessary to address the case in which
            if lastnames:                                                                                        #   the string name contains only one words (e.g. only the last name of the author is available)
                rep_dict['{Aall}'] = ", ".join(lastnames)
                rep_dict['{A3etal}'] = ", ".join(lastnames[0:3])
                if len(lastnames)>3:
                    rep_dict['{A3etal}'] = rep_dict['{A3etal}'] + " et al."
                rep_dict['{Aetal}'] = lastnames[0] + (" et al." if len(lastnames)>1 else "")

                if firstnames: 
                    firstinitials = [firstname[0][0].upper()+"."  if len(firstname[0])>0 else "" for firstname in firstnames]
                    firstinitial_lastnames = [firstinitials + " " + lastname for (firstinitials,lastname) in zip(firstinitials,lastnames) ]
  
                    rep_dict['{aAall}'] = ", ".join(firstinitial_lastnames)
                    rep_dict['{aA3etal}'] = ", ".join(firstinitial_lastnames[0:3])
                    if len(firstinitial_lastnames)>3:
                        rep_dict['{aA3etal}'] = rep_dict['{aA3etal}'] + " et al."
                    rep_dict['{aAetal}'] = firstinitial_lastnames[0] + (" et al." if len(firstinitial_lastnames)>1 else "")
                else:
                    rep_dict['{aAall}'] = rep_dict['{Aall}']
                    rep_dict['{aA3etal}'] = rep_dict['{A3etal}']
                    rep_dict['{aAetal}'] = rep_dict['{Aetal}']
            else:
                for tag in ListAuthorTags:
                    rep_dict[tag] = '[NoAuthor]'

        else: #if author_info evalues to False, it means that it is an empty string, and thus the 'author' or 'authors' tags were not present
              # in the bibtex entry
            for tag in ListAuthorTags:
                rep_dict[tag] = '[NoAuthor]'

        #Check that none of the author strings is longer than max_length_authors. If they are, we truncate it
        for tag in ListAuthorTags:
            if tag in rep_dict.keys():
                rep_dict[tag] = rep_dict[tag][0:config.get('max_length_authors')]

 
    if '{T}' in rep_dict.keys():
        if ('title' in infos) and infos['title']:
            rep_dict['{T}'] = infos['title']
        else:
            rep_dict['{T}'] = '[NoTitle]'

    for key in rep_dict.keys():
        format = format.replace(key, rep_dict[key])

    filename = sanitize(format)
    #Check that the filename string is not longer than max_length_filename, and truncate it in case. 
    filename = filename[0:config.get('max_length_filename')]
    return filename