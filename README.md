# Scientific Paper Rename (sci-paper-rename)

Tired of messy filenames for all your scientific papers? **sci-paper-rename** is here to help! This handy command-line tool automatically renames your PDFs using their actual paper titles — no more guesswork or manual renaming.

![sci-paper-rename](./img/renamer.png)

Just run it on your folder of papers, and watch it tidy up your files with neat, meaningful names. Easy, fast, and stress-free!


## Introduction

Scientific Paper Rename (or **sci-paper-rename**, for short) is a command-line tool that makes organizing your scientific papers a breeze. It scans each PDF to find the paper’s title and then renames the file to match — so your folders stay neat and easy to navigate.

## Approach

**_sci-paper-rename_** looks for the title in two places:

1. **PDF Metadata**: If the PDF was carefully created, the title might be stored in its metadata.
2. **Largest Font on First Page**: If metadata is unavailable or unreliable, the tool scans the first page of the paper, looking for a sentence with the **largest font size**, assuming it's the title.

If both methods succeed, the user is prompted to choose which title to use.

## Dependencies

The current version depends on **Python 3.11.6** and **PyMuPDF 1.26.0**. 
Please make sure to have them installed before running the package!

If your version doesn't match, use [pyenv](https://github.com/pyenv/pyenv) to install Python version 3.11.6.

## Installation

You can install **sci-paper-rename** easily with pip:

### From [PyPI](https://pypi.org/project/sci-paper-rename/)

```bash
pip install sci-paper-rename
```

### From GitHub repository (latest development version)

```bash
pip install git+https://github.com/heversonbr/sci-paper-rename.git
```

### Or, if you prefer to install locally after cloning

```bash
git clone https://github.com/heversonbr/sci-paper-rename.git
cd sci-paper-rename
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

## Usage

After installation, use the tool from the command line.


**Rename all files in a directory**

```bash
python3 sci-paper-rename.py </path/to/target_directory>
```

**Rename a single PDF file**

```bash
sci-paper-rename /path/to/specific-paper.pdf
```

**Show help message**

```bash
sci-paper-rename --help
```