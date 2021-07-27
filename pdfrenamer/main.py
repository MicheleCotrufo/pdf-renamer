import argparse
import logging
import bibtexparser
import pathlib
import os
import pdf2doi
from argparse import RawTextHelpFormatter
import itertools
import pkgutil
from pdfrenamer.config import Config
from pdfrenamer.filename_creators import build_filename, AllowedTags, check_format_is_valid

logger = logging.getLogger("pdf-renamer")

def rename(target, verbose = Config.params['verbose'], check_subfolders = False,
           format               =   Config.params['format'], 
           max_length_authors   =   Config.params['max_length_authors'], 
           max_length_filename  =   Config.params['max_length_filename'],
           numb_results_google_search   =   Config.params['numb_results_google_search'],
           tags=None):
    '''
    This is the main routine of the script. When the library is used as a command-line tool (via the entry-point "pdfrenamer") the input arguments
    are collected, validated and sent to this function (see the function main () below). 
    The function tries to rename the pdf file whose path is specified in the input argument target with the format specified in the input 
    argument format. The info of the paper (title, authors, etc.) are obtained via the library pdf2doi. 
    If the input argument target is the path of a folder, the function is applied to each pdf file contained in the folder
    (by calling again the same function). If check_subfolders is set to True, it also renames pdf files in all subfolders (recursively).

    Parameters
    ----------
    target : string
        Relative or absolute path of the target .pdf file or directory
    verbose : boolean, optional
        Increases the output verbosity. The default is False.
    check_subfolders : boolean, optional
        If set true, and if target is a directory, all sub-directories will be scanned for pdf files to be renamed. Default value is False.
    format : string, optional
        Specifies the format of the filename. If not specified, the default value Config.params['format'] is used instead.
    max_length_authors : integer, optional
        Sets the maximum length of any string related to authors. If not specified, the default value Config.params['max_length_authors'] is used instead.
    max_length_filename : integer, optional
        Sets the maximum length of any generated filename. Any filename longer than this will be truncated. If not specified, 
        the default value Config.params['max_length_filename'] is used instead.
    numb_results_google_search : integer, optional
        Set how many results should be considered when doing a google search for the paper identifier via the pdf2doi library.
        If not specified, the default value Config.params['numb_results_google_search'] is used instead.
    Returns
    -------
    results, dictionary or list of dictionaries (or None if an error occured)
        The output is a single dictionary if target is a file, or a list of dictionaries if target is a directory, 
        each element of the list describing one file. Each dictionary has the following keys
        result['path_original'] = path of the pdf file (with the original filename)
        result['path_new'] = path of the pdf file, with the new filename, or None if it was not possible to generate a new filename
        result['identifier'] = DOI or other identifier (or None if nothing is found)
        result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
        result['validation_info'] = Additional info on the paper possibly returned by the pdf2doi library
        result['bibtex_data'] = dictionary containing all available bibtex info of this publication. E.g., result['bibtex_info']['author'], result['bibtex_info']['title'], etc.
        result['method'] = method used to find the identifier

    '''
    
    # Setup logging
    if verbose: loglevel = logging.INFO
    else: loglevel = logging.CRITICAL

    logger = logging.getLogger("pdf-renamer")
    logger.setLevel(level=loglevel)
    
    #Make some sanity check on the format
    tags = check_format_is_valid(format)
    if tags == None:
        return None

    #Check if path is valid
    if not(os.path.exists(target)):
        logger.error(f"{target} is not a valid path to a file or a directory.")
        return
    
    #Check if target is a directory
        # If yes, we look for all the .pdf files inside it, and for each of them
        # we call again this function by passing the file path as target.
        #
        # Moreover, if check_subfolders==True, for each subfolder in the directory we call again this function
        # by passsing the subfolder as target

    if  os.path.isdir(target):
        logger.info(f"Looking for pdf files and subfolders in the folder {target}...")
        if not(target.endswith(os.path.sep)): #Make sure the path ends with "\" or "/" (according to the OS)
                target = target + os.path.sep

        #We build a list of all the pdf files in this folder, and of all subfolders
        pdf_files = [f for f in os.listdir(target) if (f.lower()).endswith('.pdf')]
        subfolders = [ f.path for f in os.scandir(target) if f.is_dir() ]

        numb_files = len(pdf_files)
        if numb_files == 0:
            logger.error("No pdf file found in this folder.")
        else:
            logger.info(f"Found {numb_files} pdf file(s).")

            
            files_processed = [] #For each pdf file in the target folder we will store a dictionary inside this list
            for f in pdf_files:
                logger.info(f"................") 
                file = target + f
                #We call again this same function but this time targeting the single file
                result = rename(file, verbose=verbose, format=format, 
                                max_length_filename=max_length_filename, max_length_authors= max_length_authors, 
                                tags=tags)
                files_processed.append(result)
            logger.info("................") 

        #If there are subfolders, and if check_subfolders==True, we call gain this function for each subfolder
        numb_subfolders = len(subfolders)
        if numb_subfolders:
            logger.info(f"Found {numb_subfolders} subfolder(s)")
            if check_subfolders==True :
                logger.info("Exploring subfolders...") 
                for subfolder in subfolders:
                    result = rename(subfolder, verbose=verbose, format=format, 
                                    max_length_filename=max_length_filename, max_length_authors= max_length_authors, 
                                    check_subfolders=True,
                                    tags=tags)
                    files_processed.extend(result)
            else:
                logger.info("The subfolder(s) will not be scanned because the parameter check_subfolders is set to False."+
                            " When using this script from command line, use the option -sf to explore also subfolders.") 
            logger.info("................") 
        return files_processed
    
    #If target is not a directory, we check that it is an existing file and that it ends with .pdf
    else:
        filename = target
        logger.info(f"File: {filename}")  
        if not os.path.exists(filename):
            logger.error(f"'{filename}' is not a valid file or directory.")
            return None    
        if not (filename.lower()).endswith('.pdf'):
            logger.error("The file must have .pdf extension.")
            return None
        
        #We use the pdf2doi library to retrieve the identifier and info of this file
        logger.info(f"Calling the pdf2doi library to retrieve identifier and info of this file.")
        result = pdf2doi.pdf2doi(   filename ,verbose=verbose,
                                    websearch=True, webvalidation=True,
                                    numb_results_google_search= numb_results_google_search)
        result['path_original'] = filename

        #if pdf2doi was able to find an identifer, and thus to retrieve the bibtex data, we use them to rename the file
        if result and result['identifier']:
            logger.info(f"Found an identifier for this file: {result['identifier']} ({result['identifier_type']}).")
            metadata = result['bibtex_data']
            metadata_string = "\n\t\t"+"\n\t\t".join([f"{key} = \"{metadata[key]}\"" for key in metadata.keys()] ) 
            logger.info("Found the following info:" + metadata_string)

            #Generate the new name by calling the function build_filename
            NewName = build_filename(metadata, format, tags, max_length_filename=max_length_filename, max_length_authors= max_length_authors)
            ext = os.path.splitext(filename)[-1].lower()
            directory = pathlib.Path(filename).parent
            NewPath = str(directory) + os.path.sep + NewName
            NewPathWithExt = NewPath + ext
            logger.info(f"The new file name is {NewPathWithExt}")
            if (filename==NewPathWithExt):
                logger.info("The new file name is identical to the old one. Nothing will be changed")
                result['path_new'] = NewPathWithExt
            else:
                try:
                    NewPathWithExt_renamed = rename_file(filename,NewPath,ext) 
                    logger.info(f"File renamed correctly.")
                    if not (NewPathWithExt == NewPathWithExt_renamed):
                        logger.info(f"(Note: Another file with the same name was already present in the same folder, so a numerical index was added at the end).")
                    result['path_new'] = NewPathWithExt_renamed
                except Exception as e: 
                    logger.error('Some error occured while trying to rename this file: \n '+ str(e))
                    result['path_new'] = None
        else:
            logger.info("The pdf2doi library was not able to find an identifier for this pdf file.")
            result['path_new'] = None
        
        return result 

def rename_file(old_path,new_path,ext):
    #It renames the file in old_path with the new name contained in new_path. 
    #If another file with the same name specified by new_path already exists in the same folder, it adds an 
    #incremental number (e.g. "filename.pdf" becomes "filename (2).pdf")

    if not os.path.exists(old_path):
        raise ValueError(f"The file {old_path} does not exist")
    i=1

    while True:
        New_path = new_path + (f" ({i})" if i>1 else "") + ext
        if os.path.exists(New_path):
            i = i+1
            continue
        else:
            os.rename(old_path,New_path)
            return New_path

def add_abbreviations(path_abbreviation_file):
    #Adds the content of the text file specified by the path path_abbreviation_file at the beginning of the file UserDefinedAbbreviations.txt
    if not(os.path.exists(path_abbreviation_file)):
        logger.error(f"{path_abbreviation_file} is not a valid path to a file.")
        return

    logger.info(f"Loading the file {path_abbreviation_file}...")
    try:
        with open(path_abbreviation_file, 'r') as new_abbreviation_file:
            new_abbreviation = new_abbreviation_file.read()
    except Exception as e: 
        logger.error('Some error occured while loading this file: \n '+ str(e))
        return

    logger.info(f"Adding the content of the file {path_abbreviation_file} to the user-specified journal abbreviations...")

    try:
        path_current_directory = os.path.dirname(__file__)
        path_UserDefinedAbbreviations = os.path.join(path_current_directory, 'UserDefinedAbbreviations.txt')
        with open(path_UserDefinedAbbreviations, 'r') as UserDefinedAbbreviations_oldfile:
            UserDefinedAbbreviations_old = UserDefinedAbbreviations_oldfile.read()
        with open(path_UserDefinedAbbreviations, 'w') as UserDefinedAbbreviations_newfile:
            UserDefinedAbbreviations_newfile.write( new_abbreviation )
            UserDefinedAbbreviations_newfile.write('\n')
            UserDefinedAbbreviations_newfile.write( UserDefinedAbbreviations_old )
    except Exception as e: 
        logger.error('Some error occured: \n '+ str(e))
        return

    logger.info(f"The new journal abbreviations were correctly added.")



#def set_default_values(format, max_length_authors, max_length_filename, numb_results_google_search):
#    #Verifies that the input arguments are valid, and then stores them into the .ini setting file
#    logger.info("Storing the following settings as default values:")
#    params = dict()
#    if format:
#        if check_format_is_valid(format)==None:
#            logger.error("The format specified is not valid, and therefore it will not be stored as default")
#        else:
#            params["format"] = format
#            logger.info(f"The format '{format}' has been stored as default.")

#    if max_length_authors:
#        if not(isinstance(max_length_authors,int) and max_length_authors>0):
#            logger.error("The value specified for max_length_authors is not valid (must be a positive integer)")
#        else:
#            params["max_length_authors"] = max_length_authors
#            logger.info(f"The default value of max_length_authors has been set to {max_length_authors}.")

#    if max_length_filename:
#        if not(isinstance(max_length_filename,int) and max_length_filename>0):
#            logger.error("The value specified for max_length_filename is not valid (must be a positive integer)")
#        else:
#            params["max_length_filename"] = max_length_filename
#            logger.info(f"The default value of max_length_filename has been set to {max_length_filename}.")

#    if numb_results_google_search:
#        if not(isinstance(max_length_filename,int) and max_length_filename>0):
#            logger.error("The value specified for numb_results_google_search is not valid (must be a positive integer)")
#        else:
#            params["numb_results_google_search"] = numb_results_google_search
#            logger.info(f"The default value of numb_results_google_search has been set to {numb_results_google_search}.")

#    if len(params)>0:
#        config.SetParamsINIfile(params)
#    else:
#        logger.info(f"No default value has been changed.")



def main():
    parser = argparse.ArgumentParser( 
                                    description = "Automatically renames pdf files of scientific publications by retrieving their identifiers (e.g. DOI or arxiv ID) and looking up their bibtex infos.",
                                    epilog = "",
                                    formatter_class=RawTextHelpFormatter)
    parser.add_argument(
                        "path",
                        help = "Relative path of the pdf file or of a folder.",
                        metavar = "path",
                        nargs = '*')
    parser.add_argument(
                        "-nv",
                        "--no_verbose",
                        help="Decrease verbosity of output.",
                        action="store_true")
    parser.add_argument('-f', 
                        help=f"Format of the new filename. Default = \"{Config.params['format']}\".\n"+
                        "Valid tags:\n"+
                        "\n".join([key+val for key,val in AllowedTags.items()]),
                        action="store", dest="format", type=str, default=Config.params['format'])
    parser.add_argument("-sf",
                        "--sub_folders",
                        help="Rename also pdf files contained in subfolders of target folder.",
                        action="store_true")
    parser.add_argument('-max_length_authors', 
                        help=f"Sets the maximum length of any string related to authors (default={str(Config.params['max_length_authors'])}).",
                        action="store", dest="max_length_authors", type=int, default=Config.params['max_length_authors'])
    parser.add_argument('-max_length_filename', 
                        help=f"Sets the maximum length of any generated filename. Any filename longer than this will be truncated (default={str(Config.params['max_length_filename'])}).",
                        action="store", dest="max_length_filename", type=int, default=Config.params['max_length_filename'])
    parser.add_argument('-numb_results_google_search', 
                        help=f"Set how many results should be considered when doing a google search for the paper identifier via the pdf2doi library (default={str(Config.params['numb_results_google_search'])}).",
                        action="store", dest="numb_results_google_search", type=int, default=Config.params['numb_results_google_search'])
    parser.add_argument(
                        "-add_abbreviation_file",
                        help="The content of the text file specified by PATH_ABBREVIATION_FILE will be added to the list of journal abbreviations.\n"+
                        "Each row of the text file must have the format \'FULL NAME = ABBREVIATION\'. Note: when this argument is passed, all other arguments are ignored.",
                        action="store", dest="path_abbreviation_file", type=str)
    parser.add_argument(
                        "-sd",
                        "--set_default",
                        help="By adding this command, any value specified (in this same command) for the filename format (-f), "+
                        "max length of author string (-max_length_authors), max length of filename string (-max_length_filename) or max number of google results (-numb_results_google_search) "+
                        "will be also stored as default value(s).",
                        action="store_true")
    parser.add_argument("-install--right--click",
                        dest="install_right_click",
                        action="store_true",
                        help="Add a shortcut to pdf-renamer in the right-click context menu of Windows. You can rename a single pdf file (or all pdf files in a folder) by just right clicking on it! NOTE: this feature is only available on Windows.")
    parser.add_argument("-uninstall--right--click",
                        dest="uninstall_right_click",
                        action="store_true",
                        help="Uninstall the right-click context menu functionalities. NOTE: this feature is only available on Windows.")

    
    args = parser.parse_args()

    #If the command -install--right--click was specified, it sets the right keys in the system registry
    if args.install_right_click:
        import pdfrenamer.utils_registry as utils_registry
        utils_registry.install_right_click()
        return
    if args.uninstall_right_click:
        import pdfrenamer.utils_registry as utils_registry
        utils_registry.uninstall_right_click()
        return

    # Setup logging
    if not(args.no_verbose): loglevel = logging.INFO
    else: loglevel = logging.CRITICAL
    logger = logging.getLogger("pdf-renamer")
    logger.setLevel(level=loglevel)

    if args.path_abbreviation_file:
        add_abbreviations(args.path_abbreviation_file)
        return

    Config.update_params({  'verbose' : not(args.no_verbose),
                            'format' : args.format,
                            'max_length_authors' : args.max_length_authors,
                            'max_length_filename' : args.max_length_filename,
                            'numb_results_google_search' : args.numb_results_google_search
                            })

    if args.set_default:
        logger.info("Storing the settings specified by users as default values...")
        Config.WriteParamsINIfile()
        logger.info("Done.")

    if isinstance(args.path,list):
        if len(args.path)>0:
            target = args.path[0]
        else:
            target = ""
    else:
        target = args.path

    if target == "" and not (args.set_default):
        print("pdfrenamer: error: the following arguments are required: path. Type \'pdfrenamer --h\' for a list of commands.")
    if target == "": #This occurs either if the user forgot to add a target, or if the user used the -sd command to set default values
        return

    results = rename(
                  target                =       target,
                  check_subfolders =            args.sub_folders
                  )

    if results==None:  #This typically happens when target is neither a valid file nor a valid directory. In this case we stop
        return         #the script execution here. Proper error message are raised by the rename function

    if  os.path.isdir(target):
        target = os.path.join(target, '') #This makes sure that, if target is a path to a directory, it has the ending "/" or "\"
    MainPath = os.path.dirname(target) #Extract the path of target. If target is a directory, then MainPath = target
    logger.info("Summaries of changes done:")    

    if not isinstance(results,list):
        results = [results]
    
    counter = 0
    counter_identifier_notfound = 0
    for result in results:
        if result and result['identifier']:
            if not(result['path_original']==result['path_new']):
                logger.info(f"\'{os.path.relpath(result['path_original'],MainPath)}\' --> \'{os.path.relpath(result['path_new'],MainPath)}\'")
                counter = counter + 1
        else : 
            counter_identifier_notfound = counter_identifier_notfound + 1
    if counter==0:
        logger.info("No file has been renamed.")
    else:
        logger.info(f"{counter} file" + ("s have " if counter>1 else " has ") + "been renamed.")

    if counter_identifier_notfound > 0:
        logger.info("The following pdf files could not be renamed because it was not possile to automatically find " +
              "the publication identifier (DOI or arXiv ID). Try to manually add a valid identifier to each file via " +
              "the command \"pdf2doi 'filename.pdf' -id 'valid_identifier'\" and then run again pdf-renamer.")  
        for result in results:
            if not(result['identifier']):
                logger.info(f"{result['path_original']}")
    return

if __name__ == '__main__':
    main()