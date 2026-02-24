This documentation explains the installation of the cleaning process for NIST files.
The aim is to remove personal information (such as the name, date of birth, police number, ...) related to the source of a NIST files.

# General considerations

The scripts are using Python2 (and not the current version of Python 3).
Moreover, some libraries are mendatory as custom libraries.
It's recommended to create a virtual environment (with the `virtualenv` command).

All the libraries have been tested on Linux only, but should work on MacOS and Windows.
The recommended way of running the scripts is via Docker; this way does not require to install anything related to the running environment manually.

# Installation

First, install Python2 (the script will not work with Python3!).
Then, we shall install the custom libraries to read NIST files.

## Python2

- Download the installation binary from www.python.org (https://www.python.org/downloads/release/python-2718/). The version x64 should work without any problems.
- Install Python2
- Test the installation by starting Python; if you have a python prompt, you are OK.

It's possible that the installation process of Python does not add the `python` command in the terminal by default.
In this case, you can use the full path for the installation binary (`C:/Python27/python.exe` in my case).

## Libraries

Some libraries shall be installed.
It's possible to install the libraries to the system level (not recommended) or in the virtual-environment (highly recommended for any machine that is not dedicated to the NIST file cleaning process).

Note: For the rest of the installation, the main working directory will be `/home/mdedonno/UNIL/NIJ-2018-DU-BX-0227/tools`.

### Virtual environment

To activate the virtual-environment, first install `virtualenv` with the pip command:

`python -m pip install virtualenv`

Then activate the virtual environment:

`python -m virtualenv venv`

This command should be executed in the working directory, and will create a `venv` folder.

From now on, the correct `python.exe` file should be used.
If you use the system python, use the full path to the system python binary; If you use the virtual-environment as installed in this paragraph, use the full path to the python binary for this virtual environment (/home/mdedonno/UNIL/NIJ-2018-DU-BX-0227/tools/venv/bin/python or the correct one for Windows).

### Download to the correct directory

The libraries can be downloaded from here:

- https://esc-md-git.unil.ch/mdedonno/MDmisc
- https://esc-md-git.unil.ch/mdedonno/WSQ
- https://esc-md-git.unil.ch/mdedonno/PMlib
- https://esc-md-git.unil.ch/mdedonno/NIST

The easiest way to make the installation is to clone the repositories with `git` in a dedicated folder.

The content of the libraries can also be downloaded via the `download zip file` on the pages.

Once downloaded, the file structure should be similar to this one:

```
/home/mdedonno/UNIL/NIJ-2018-DU-BX-0227/tools

├── Readme.md
├── libraries
│   ├── MDmisc
│   │   ├── doctester.py
│   │   ├── __init__.py
│   │   ├── LICENSE
│   │   ├── MDmisc
│   │   └── requirements.txt
│   ├── NIST
│   │   ├── CHANGELOG.txt
│   │   ├── doc
│   │   ├── doctester2.py
│   │   ├── doctester.py
│   │   ├── __init__.py
│   │   ├── LICENSE
│   │   ├── NIST
│   │   ├── readme.rst
│   │   ├── requirements.txt
│   │   ├── TODO.txt
│   │   └── update.py
│   ├── PMlib
│   │   ├── LICENSE
│   │   ├── PMlib
│   │   └── requirements.txt
│   └── WSQ
│       ├── __init__.py
│       ├── LICENSE
│       ├── requirements.txt
│       └── WSQ
└── venv
    ├── bin
    │   ├── activate
    │   .
    │   .
    │   .
    ├── lib
    │   ├── python2.7
    │   .   ├── site-packages
    │   .   .   ├── mdedonno.pth
    │
    └── pyvenv.cfg
```

With `libraries` the folder containing the libraries, and `venv` the folder with the virtual environment.

Note the presence of the `mdedonno.pth` file in the `venv/lib/python2.7/site-packages/`.
On Windows, the `mdedonno.pth` file could also be present in the `venv/Lib/site-packages` folder.
The installation of the custom libraries is done in the `mdedonno.pth` file; this file should be added manually.

This file is very important in the installation process of the libraries.

### Install the libraries

The content of the `mdedonno.pth` file is as follow:

```
/home/mdedonno/UNIL/NIJ-2018-DU-BX-0227/tools/libraries/NIST
/home/mdedonno/UNIL/NIJ-2018-DU-BX-0227/tools/libraries/PMlib
/home/mdedonno/UNIL/NIJ-2018-DU-BX-0227/tools/libraries/WSQ
/home/mdedonno/UNIL/NIJ-2018-DU-BX-0227/tools/libraries/MDmisc
```

This link to the full path of the directories containing the libraries.

### Enable the `venv`

To use this tool, the `venv` should be enable with the following command

``` bash
source venv/bin/activate
```

On a Windows machine, the script should be located here: `\env\Scripts\activate.bat`.

### Install the libraries dependencies

With the virtual environment activated, you should execute the following command `pip install -r requirements.txt` in each of the 4 libraries directories.

Once the 4 requirements.txt files installed, you should be able to run python and test the installation with:

``` bash
(venv) mdedonno @ yoga: ~/UNIL/NIJ-2018-DU-BX-0227/tools/clean_nist_files (master)
$ python
Python 2.7.18 (default, Apr 20 2020, 20:30:41)
[GCC 9.3.0] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import numpy
>>>
```

If you dont have an error, the dependencies are (probably) installed correctly.

### Test of the installation

To test the NIST library, you can open python from the terminal with the `python` command, and try to `import NIST`:

``` bash
(venv) mdedonno @ yoga: ~/UNIL/NIJ-2018-DU-BX-0227/tools/clean_nist_files (master)
$ python
Python 2.7.18 (default, Apr 20 2020, 20:30:41)
[GCC 9.3.0] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import NIST
>>> print(NIST.__version__)
dev
>>>
```

If no error is displayed, the installation should be done correctly.
Note that the version may be different for your installation.

# Usage

To clean the NIST files, you should use the `clean_files.py` script.
This script expect two modifications:

```
input_directory = ""
output_directory = ""
```

Those folders shall be the full path of the folders containing the files to be processed (`input_directory`) and the output directory (`output_directory`).

Once the script has been read and updated as needed, it can be run with a `python clean_files.py` command.

This script will take one directory as input, load all the files, remove all the PII informations, and write the files in a second directory.

# Check the cleaning process

To check the content of the NIST file, use the `check_nist_file.py` script.
This file should be updated to point the `nist_file_path` to the file on disk.

By printing the `nist_file` object, the content of the file is outputted to the console.
All the fields are displayed, on the left the field tag, and on the right the content of the field.

If one field present in the output should be delete, update the `clean_files.py` file accordingly.

