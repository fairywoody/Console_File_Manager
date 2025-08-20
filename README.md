# DirTools - Command Line File Manager

DirTools is a command-line utility for managing files and directories with various features such as copying, moving, deleting, counting files, searching by regex, adding date prefixes, analyzing directory size, hashing files and directories, and finding duplicate files.

This project uses only Python standard libraries:
os, sys, shutil, argparse, hashlib, logging, etc.
No external dependencies required.

## Features

- Copy, move, and delete files.
- Check folder content
- Count files in a directory.
- Add date prefix to filenames.
- Analyze directory content size.

## Examples

### For help run:
bash

python manager.py -h

python manager.py <command> -h
### Copy file or folder
bash
python manager.py copy /path/to/source/file.txt /path/to/destination/folder
### Count files
bash
python manager.py count /path/to/directory

or to include directories in count

python manager.py count -d /path/to/directory
### Delete file or folder

bash
python manager.py delete_file /path/to/source/file.txt
### Move file or folder
bash

python manager.py move /path/to/source/file.txt /path/to/destination/folder
### Add date to filename
bash

python manager.py add_date /path/to/file.txt

or to change date in every file in directory (and subfolders)

python manager.py add_date -r /path/to/directory
### Analyse file or folder
bash

python manager.py list /path/to/directory

or to see the list with hidden files

python manager.py list -a /path/to/directory 

or to analyse file or folder

python manager.py list -l /path/to/directory
## Installation

1. Clone the repository:

bash

git clone https://github.com/yourusername/dirtools.git

cd dirtools
