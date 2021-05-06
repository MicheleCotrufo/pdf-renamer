import setuptools
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open("requirements.txt") as f:
    required_packages = f.read().splitlines()

setuptools.setup(name='pdf_renamer',
      version='0.1',
      description='A python library/command-line tool to automatically rename the pdf files of scientific publications.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/MicheleCotrufo/pdf_renamer',
      author='Michele Cotrufo',
      author_email='michele.cotrufo@gmail.com',
      license='MIT',
      entry_points = {
        'console_scripts': ["renamepdf = pdf_renamer.pdf_renamer:main"],
      },
      packages=['pdf_renamer'],
      include_package_data=True ,
      install_requires= required_packages,
      zip_safe=False)