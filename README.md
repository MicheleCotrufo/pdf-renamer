# pdf2doi

pdf2doi is a Python library to extract the DOI or other identifiers (e.g. arXiv) starting from the .pdf file of a publication (or from a folder containing several .pdf files).
It exploits several methods (see below for detailed description) to find a possible identifier, and it validates any result
via web queries to public archives (e.g. http://dx.doi.org). Additionally, it allows generating automatically bibtex entries.
(Note: in the current version only the format of arXiv identifiers in use after [1 April 2007](https://arxiv.org/help/arxiv_identifier) is supported) 


## Description
Automatically associating a DOI or other identifiers (e.g. arXiv) to a pdf file can be either a very easy or a very difficult
(sometimes nearly impossible) task, depending on how much care was placed in crafting the file. In the simplest case (which typically applies to most recent publications)
it is enough to look into the file metadata. For older publications, the identifier is often found within the pdf text and it can be
extracted with the help of regular expressions. In the unluckiest cases, the only method left is to google some details of the publication
(e.g. the title or parts of the text) and hope that a valid identifier is contained in one of the first results.

The ```pdf2doi``` library applies sequentially all these methods (starting from the simpler one) until a valid identifier is found and validated.
Specifically, for a given .pdf file it will, in order,

1. Look into the metadata of the .pdf file (extracted via the library [PyPDF2](https://github.com/mstamy2/PyPDF2)) and see if any string matches the pattern of 
a DOI or an arXiv ID. Priority is given to the metadata which contain the word 'doi' in their label.

2. Check if the name of the pdf file contains any sub-string that matches the pattern of 
a DOI or an arXiv ID.

3. Scan the text inside the .pdf file, and check for any string that matches the pattern of 
a DOI or an arXiv ID. The text is extracted with the libraries [PyPDF2](https://github.com/mstamy2/PyPDF2) and [textract](https://github.com/deanmalmgren/textract).

4. Try to find possible titles of the publication. In the current version, possible titles are identified via 
the library [pdftitle](https://github.com/metebalci/pdftitle "pdftitle"), and by the file name. For each possible title a google search 
is performed and the plain text of the first results is scanned for valid identifiers.

5. As a last desperate attempt, the first N=1000 characters of the pdf text are used as a query for
a google search (the value of N can be set by the variable config.N_characters_in_pdf). The plain text of the first results is scanned for valid identifiers.


## Installation

Use the package manager pip to install pdf2doi.

```bash
pip install pdf2doi
```

## Usage

pdf2doi can be used either as a stand-alone application invoked from the command line, or by importing it in your python project.

### Usage inside a python script:
The function ```pdf2doi``` can be used to look for the identifier of a pdf file by applying all the available methods. Setting ```verbose=True``` will increase the output verbosity, documenting all steps performed.
```python
import pdf2doi
result = pdf2doi.pdf2doi('.\examples\PhysRevLett.116.061102.pdf',verbose=True)
print('\n')
print(result['identifier'])
print(result['identifier_type'])
print(result['method'])
```
 The previous code produces the output
```
................
File: .\examples\PhysRevLett.116.061102.pdf
Looking for a valid identifier in the document infos...
Could not find a valid identifier in the document info.
Looking for a valid identifier in the file name...
Could not find a valid identifier in the file name.
Looking for a valid identifier in the document text...
Extracting text with the library PyPdf...
Validating the possible DOI 10.1103/PhysRevLett.116.061102 via a query to dx.doi.org...
The DOI 10.1103/PhysRevLett.116.061102 is validated by dx.doi.org. A bibtex entry was also created.
A valid DOI was found in the document text.

10.1103/PhysRevLett.116.061102
DOI
document_text
```

The output variable ```result``` is a dictionary containing the identifier and other relevant information,
```
result['identifier'] =      DOI or other identifier (or None if nothing is found)
result['identifier_type'] = string specifying the type of identifier (e.g. 'doi' or 'arxiv')
result['validation_info'] = Additional info on the paper. If the online validation is enabled, then result['validation_info']
                            will typically contain a bibtex entry for this paper. Otherwise it will just contain True                         
result['path'] =            path of the pdf file
result['method'] =          method used to find the identifier
```

The first argument passed to the function ```pdf2doi``` can also be a directory. In this case the function will 
look for all valid pdf files inside the directory, try to find a valid identifier for each of them,
and return a list of dictionaries.

For example, the code 
```python
import pdf2doi
results = pdf2doi.pdf2doi('.\examples')
for result in results:
    print(result['identifier'])
```
produces the output
```
10.1103/PhysRevLett.116.061102
10.1103/PhysRevLett.76.1055
10.1038/s41586-019-1666-5
```
Additional arguments can be passed to the function ```pdf2doi``` to control its behaviour, e.g. to specify if
web-based methods should not be used (either to find an identifier and/or to validate it).

```
def pdf2doi(target, verbose=False, websearch=True, webvalidation=True,
                numb_results_google_search=config.numb_results_google_search,
                filename_identifiers = False, filename_bibtex = False):
    '''
    Parameters
    ----------
    target : string
        Relative or absolute path of the target .pdf file or directory
    verbose : boolean, optional
        Increases the output verbosity. The default is False.
    websearch : boolean, optional
        If set false, any method to find an identifier which requires a web search is disabled. The default is True.
    webvalidation : boolean, optional
        If set false, validation of identifier via internet queries (e.g. to dx.doi.org or export.arxiv.org) is disabled. 
        The default is True.
    numb_results_google_search : integer, optional
        It sets how many results are considered when performing a google search. The default is config.numb_results_google_search.
    filename_identifiers : string or boolean, optional
        If is set equal to a string, all identifiers found in the directory specified by target are saved into a text file 
        with a path specified by filename_identifiers. The default is False. It is ignored if the input parameter target is a file.
    filename_bibtex : string or boolean, optional
        If is set equal to a string, all bibtex entries obtained in the validation process for the pdf files found in the 
        directory specified by target are saved into a text file with a path specified by filename_bibtex. 
        The default is False. It is ignored if the input parameter target is a file.
```

The online validation of an identifier relies on performing queries to different online archives 
(e.g. dx.doi.org for DOIs or export.arxiv.org for arXiv identifiers). Using data obtained from these queries, a bibtex entry is created
and stored in the 'validation_info' element of the output dictionary. By setting the input argument ```filename_bibtex``` equal to a 
valid filename, the bibtex entries of all papers in the target directory will be saved in a file within the same directory.

For example,
```python
import pdf2doi
results = pdf2doi.pdf2doi('.\examples',filename_bibtex='bibtex.txt')
```
creates the file [bibtex.txt](/examples/bibtex.txt) in the 'examples' folder.

### Command line usage:
The library can also be used directly from the command line, without having to open a python console.

- Find and print the identifier of a single paper, outputting all logs:

```
>>pdf2doi '.\examples\PhysRevLett.116.061102.pdf'
```

- Find and print the identifiers of all pdf files contanined in a folder:
```
>>pdf2doi '.\examples\' --no_verbose
```

- Find the identifiers of all pdf files contanined in a folder and create a text file with all the bibtex entries:
```
>>pdf2doi '.\examples\' -b 'bibtex.txt' --no_verbose
```

The syntax for the command-line invokation follows closely the arguments that can be passed to the pdf2doi python function,

```
>> pdf2doi --h
usage: pdf2doi [-h] [-nv] [-nws] [-nwv] [-google_results GOOGLE_RESULTS] [-s [FILENAME_IDENTIFIERS]]
               [-b [FILENAME_BIBTEX]]
               path

Retrieves the DOI or other identifiers (e.g. arXiv) from pdf files of a publications.

positional arguments:
  path                  Relative path of the pdf file or of a folder.

optional arguments:
  -h, --help            show this help message and exit
  -nv, --no_verbose     Decrease verbosity.
  -nws, --nowebsearch   Disable any DOI retrieval method which requires internet searches (e.g. queries to google).
  -nwv, --nowebvalidation
                        Disable the DOI online validation via queries (e.g., to http://dx.doi.org/).
  -google_results GOOGLE_RESULTS
                        Set how many results should be considered when doing a google search for the DOI (default=6).
  -s [FILENAME_IDENTIFIERS], --save_identifiers [FILENAME_IDENTIFIERS]
                        Save all the DOIs/identifiers found in the target folder in a .txt file inside the same folder
                        (only available when a folder is targeted).
  -b [FILENAME_BIBTEX], --make_bibtex [FILENAME_BIBTEX]
                        Create a file with bibtex entries for each .pdf file in the targer folder (for which a valid
                        identifier was found). This option is only available when a folder is targeted, and when the
                        web validation is allowed.
```


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[MIT](https://choosealicense.com/licenses/mit/)