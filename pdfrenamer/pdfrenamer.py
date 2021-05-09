import argparse
import logging
import bibtexparser
from os import path, listdir
import pathlib
import os
import pdf2doi
from argparse import RawTextHelpFormatter
import pkgutil
import pdfrenamer.config as config
from pdfrenamer.filename_creators import build_filename, find_tags_in_format, AllowedTags 

def rename(target, verbose=False, format=config.format, 
           max_length_authors=config.max_length_authors, max_length_filename=config.max_length_filename,
           check_subfolders = False,
           tags=None):
    '''
    This is the main routine of the script
    Parameters
    ----------
    target : string
        Relative or absolute path of the target .pdf file or directory
    verbose : boolean, optional
        Increases the output verbosity. The default is False.
    format : string, optional
        Specifies the format of the filename. If not specified, the default value config.format is used instead.
    max_length_authors : integer, optional
        Sets the maximum length of any string related to authors. If not specified, the default value config.max_length_authors is used instead.
    max_length_filename : integer, optional
        Sets the maximum length of any generated filename. Any filename longer than this will be truncated. If not specified, 
        the default value config.max_length_filename is used instead.
    check_subfolders : boolean, optional
        If set true, and if target is a directory, all sub-directories will be scanned for pdf files to be renamed. Default value is False.

    Returns
    -------
    results, dictionary or list of dictionaries (or None if an error occured)
        The output is a single dictionary if target is a file, or a list of dictionaries if target is a directory, 
        each element of the list describing one file. Each dictionary has the following keys
        result['path_original'] = path of the pdf file (with the original filename)
        result['path_new'] = path of the pdf file (with the new filename)
        result['identifier'] = DOI or other identifier (or None if nothing is found)
        result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
        result['validation_info'] = Additional info on the paper possibly returned by the pdf2doi library
        result['method'] = method used to find the identifier

    '''
    
    #config.numb_results_google_search = numb_results_google_search

    # Setup logging
    if verbose: loglevel = logging.INFO
    else: loglevel = logging.CRITICAL

    logger = logging.getLogger("pdf-renamer")
    logger.setLevel(level=loglevel)
    
    #Make some sanity check on the format
    if not format:
        logger.error(f"The specified format is not a valid string.")
        return None
    tags = find_tags_in_format(format)
    if not tags:
        logger.error(f"The specified format does not contain any tag.")
        return None
    for tag in tags:
        if not tag in AllowedTags:
            logger.error(f"The specified format contains \"{tag}\", which is not a valid tag.")
            return None
    
    #Check if target is a directory
        #If yes, we look for all the .pdf files inside it, and for each of them
        #we call again this function by passing the file path as target..
        #Moreover, if check_subfolders==True, for each subfolder in the directory we call again this function
        #by passsing the subfolder as target

    if  path.isdir(target):
        logger.info(f"Looking for pdf files in the folder {target}...")
        pdf_files = [f for f in listdir(target) if f.endswith('.pdf')]
        if check_subfolders==True:
            subfolders = [ f.path for f in os.scandir(target) if f.is_dir() ]

        numb_files = len(pdf_files)
        
        if numb_files == 0:
            logger.error("No pdf files found in this folder.")
            return None
        
        logger.info(f"Found {numb_files} pdf files.")
        if not(target.endswith(config.separator)): #Make sure the path ends with "\" or "/" (according to the OS)
            target = target + config.separator
            
        files_processed= [] #For each pdf file in the target folder we will store a dictionary inside this list

        if path.exists(target + "journal_abbreviations.txt"):
            logger.info(f"Found a file journal_abbreviations.txt with possible additional Journal abbreviations.")
            config.additional_abbreviations_file = target + "journal_abbreviations.txt"

        for f in pdf_files:
            logger.info(f"................") 
            file = target + f
            result = rename(file, verbose=verbose, format=format, 
                            max_length_filename=max_length_filename, max_length_authors= max_length_authors, 
                            tags=tags)
            #logger.info(result['identifier'])
            files_processed.append(result)
        logger.info("................") 

        if check_subfolders==True:
            if subfolders: logger.info("Exploring subfolders...") 
            for subfolder in subfolders:
                result = rename(subfolder, verbose=verbose, format=format, 
                                max_length_filename=max_length_filename, max_length_authors= max_length_authors, 
                                check_subfolders=True, tags=tags)
                files_processed.append(result)

        

        return files_processed
    
    #If target is not a directory, we check that it is an existing file and that it ends with .pdf
    else:
        filename = target
        logger.info(f"File: {filename}")  
        if not path.exists(filename):
            logger.error(f"'{filename}' is not a valid file or directory.")
            return None    
        if not filename.endswith('.pdf'):
            logger.error("The file must have .pdf extension.")
            return None
        
        #We use the pdf2doi library to retrieve the identifier and info of this file
        logger.info(f"Calling the pdf2doi library to retrieve identifier and info of this file.")
        result = pdf2doi.pdf2doi(   filename ,verbose=verbose,
                                    websearch=True, webvalidation=True,
                                    numb_results_google_search=config.numb_results_google_search)
        result['path_original'] = filename
        if result and result['identifier']:
            logger.info(f"Found an identifier for this file: {result['identifier']} ({result['identifier_type']}).")
            data = result['validation_info']
            data = bibtexparser.loads(data)
            metadata = data.entries[0]
            metadata_string = "\t\t\t\t"+"\n\t\t\t\t".join([f"{key} = \"{metadata[key]}\"" for key in metadata.keys()] ) 
            #logger.info("Found the following info:")
            #logger.info(metadata_string)
            NewName = build_filename(metadata, format, tags,max_length_filename=max_length_filename, max_length_authors= max_length_authors)
            ext = os.path.splitext(filename)[-1].lower()
            directory = pathlib.Path(filename).parent
            NewPath = str(directory) + config.separator + NewName
            NewPathWithExt = str(directory) + config.separator + NewName + ext
            logger.info(f"The new filename is {NewPathWithExt}")
            if (filename==NewPathWithExt):
                logger.info("The new filename is identical to the old one. Nothing will be changed")
            else:
                try:
                    NewPathWithExt_renamed = rename_file(filename,NewPath,ext) 
                    logger.info(f"File renamed correctly.")
                    if not (NewPathWithExt == NewPathWithExt_renamed):
                        logger.info(f"(Note: Another file with the same name was already present in the same folder, so a numerical index was added in the end).")
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
    #incremental number
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

def main():
    parser = argparse.ArgumentParser( 
                                    description = "Automatically renames pdf files of scientific publications by retrieving their identifiers (e.g. DOI or arxiv ID) and looking up their bibtex infos.",
                                    epilog = "",
                                    formatter_class=RawTextHelpFormatter)
    parser.add_argument(
                        "path",
                        help = "Relative path of the pdf file or of a folder.",
                        metavar = "path")
    parser.add_argument(
                        "-nv",
                        "--no_verbose",
                        help="Decrease verbosity of output.",
                        action="store_true")
    parser.add_argument('-f', 
                        help="Format of the new filename. Default = \"{YYYY} - {Jabbr} - {A3etal} - {T}\".\n"+
                        "Valid tags:\n"+
                        "\n".join([key+val for key,val in AllowedTags.items()]),
                        action="store", dest="format", type=str, default = "{YYYY} - {Jabbr} - {A3etal} - {T}")
    parser.add_argument('-max_length_authors', 
                        help=f"Sets the maximum length of any string related to authors (default={str(config.max_length_authors)}).",
                        action="store", dest="max_length_authors", type=int)
    parser.add_argument('-max_length_filename', 
                        help=f"Sets the maximum length of any generated filename. Any filename longer than this will be truncated (default={str(config.max_length_filename)}).",
                        action="store", dest="max_length_filename", type=int)
    parser.add_argument('-google_results', 
                        help=f"Set how many results should be considered when doing a google search for the paper identifier via the pdf2doi library (default={str(config.numb_results_google_search)}).",
                        action="store", dest="google_results", type=int)

    
    args = parser.parse_args()
    results = rename(target=args.path,
                  verbose=not(args.no_verbose),
                  format=args.format,
                  max_length_authors = args.max_length_authors,
                  max_length_filename = args.max_length_filename
                  )

    print("Summaries of changes done:")    
    if not results:
        print("No file has been renamed.")
        return

    if not isinstance(results,list):
        results = [results]
    
    counter = 0
    for result in results:
        if result['identifier'] and not(result['path_original']==result['path_new']):
            print(f"\'{result['path_original']}\' --> \'{result['path_new']}\'")
            counter = counter + 1
    if counter==0:
        print("No file has been renamed.")
    else:
        string = f"{counter} file" + ("s have " if counter>1 else " has ") + "been renamed."
        print(string)

    return

if __name__ == '__main__':
    main()