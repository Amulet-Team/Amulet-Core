# Amulet Core

![Build](../../workflows/Build/badge.svg)
![Unittests](../../workflows/Unittests/badge.svg?event=push)
![Stylecheck](../../workflows/Stylecheck/badge.svg?event=push)
[![Documentation](https://readthedocs.org/projects/amulet-core/badge)](https://amulet-core.readthedocs.io)

A Python 3 library to read and write data from Minecraft's various save formats.

This library provides the main world editing functionality for Amulet Map Editor

#### If you are looking for the actual editor it can be found at [Amulet Map Editor](https://github.com/Amulet-Team/Amulet-Map-Editor)


## Documentation

Our online documentation can be found here: https://amulet-core.readthedocs.io

## Installing
1) Install Python 3.7
2) We recommend setting up a [python virtual environment](https://docs.python.org/3/tutorial/venv.html) so you don't run into issues with dependency conflicts.
3) run `pip install amulet-core` to install the library and all its dependencies.

## Dependencies

This library uses a number of other libraries. These will be automatically installed when running the command above.
- Numpy
- [Amulet_NBT](https://github.com/Amulet-Team/Amulet-NBT)
- [PyMCTranslate](https://github.com/gentlegiantJGC/PyMCTranslate)

## Contributing

### For Development
Download the code to your computer, install python and run the following command from the root directory.
run `pip install -e .[dev]`
This command will install the library in development mode with the libraries required for development.
- [Black](https://github.com/ambv/black) (Required for formatting)
  - Must be run before pushing a Pull Request

For information about contributing to this project, please see the contribution section [below](#contributing)

### Code Formatting
For code formatting, we use the formatting utility [black](https://github.com/psf/black). 
To run it, run the following command from your favorite terminal after installing: `black amulet tests`

In order for your pull request to be accepted, this command must be run to format every file.

### Building the Documentation
To build the documentation locally, run the following command: `make html` and then navigate to the
generated directory `docs_build/html` in your favorite web browser

### Branch Naming
Branches should be created when a certain bug or feature may take multiple attempts to fix. Naming
them should follow the following convention (even for forked repositories when a pull request is being made):

* For features, use: `impl-<feature name>`
* For bug fixes, use: `bug-<bug tracker ID>`
* For improvements/rewrites, use: `improv-<feature name>`
* For prototyping, use: `proto-<feature name>`

### Pull Requests
We ask that submitted Pull Requests give moderately detailed notes about the changes and explain 
any changes that were made to the program outside of those directly related to the feature/bug-fix.
Make sure to run all tests and formatting otherwise we cannot accept your pull request.

_Note: We will also re-run all tests before reviewing, this is to mitigate additional changes/commits
needed to pass all tests._

Once a Pull Request is submitted, we will mark the request for review, once that is done, we will
review the changes and provide any notes/things to change. Once all additional changes have been made,
we will merge the request.
