# pdf-renamer
pdf-renamer is a Python command-line tool to automatically rename the pdf files of a scientific paper, or in general any publication which can be associated to a [DOI](http://dx.doi.org) or
other identifiers (e.g. [arXiv](https://arxiv.org)). It can be used to rename single files or to scan entire folders and sub-folders.
The format of the filename can be specified by the user by choosing among several tags. Besides command-line operation, it can also be used as a library
from your Python project. 

## Table of Contents
 - [Description](#description)
 - [Installation](#installation)
 - [Usage](#usage)
 - [Installing the shortcuts in the right-click context menu of Windows](#installing-the-shortcuts-in-the-right-click-context-menu-of-windows)
  - [Contributing](#contributing)
 - [License](#license)

## Description
```pdf-renamer``` uses the libraries [pdf2doi](https://github.com/MicheleCotrufo/pdf2doi) and [pdf2bib](https://github.com/MicheleCotrufo/pdf2bib) to extract 
bibliographic data of a paper starting from a .pdf file. The retrieved data can then be used to automatically rename pdf files with a custom format (e.g. 'Year - Journal - Authors - Title').

## Installation

[![Pip Package](https://img.shields.io/pypi/v/pdf-renamer?logo=PyPI)](https://pypi.org/project/pdf-renamer)

Use the package manager pip to install pdf-renamer.

```bash
pip install pdfrenamer==1.0rc1
```
The executable will be installed in certain directory whose path depends on the type of Python installation and the operating system. Make sure that this directory is in the ```PATH``` variable of your operating system (for standard python installations under Windows this should be already the case). Check how to do add the folder to the ```PATH``` variable for [Windows](https://www.google.com/search?q=python+add+script+folder+to+path+windows), [Mac](https://www.google.com/search?q=python+add+script+folder+to+path+mac) and [Linux](https://www.google.com/search?q=python+add+script+folder+to+path+linux).

Under Windows, it is also possible to add [shortcuts to the right-click context menu](#installing-the-shortcuts-in-the-right-click-context-menu-of-windows).

## Usage

```pdf-renamer``` can be invoked directly from the command line, without having to open a python console.
The simplest command-line invokation is

```
$ pdfrenamer 'path/to/target'
```
where ```target``` is either a valid pdf file or a directory containing pdf files.

Type

```
$ pdfrenamer --h
```

for a list of all the possible optional commands.

[TO FINISH]


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[MIT](https://choosealicense.com/licenses/mit/)