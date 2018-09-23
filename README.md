# Amulet Map Editor

<a href="https://circleci.com/gh/Podshot/Amulet-Map-Editor"><img alt="CircleCI" src="https://circleci.com/gh/Podshot/Amulet-Map-Editor.svg"></a>

A new Minecraft world editor that aims to be flexible, extendable, and support most editions
of Minecraft.

## Requirements

### For Running From Source
- Python 3.7.0+
- Numpy
- pyglet
- NBT

Shortcut: `pip -r requirements.txt`

### For Development
- [Black](https://github.com/ambv/black) (Required for formatting)
  - Must be ran before pushing a Pull Request
- Sphinx
- [sphinx-autodoc-typehints](https://github.com/agronholm/sphinx-autodoc-typehints)
- [sphinx_rtd_theme](https://github.com/rtfd/sphinx_rtd_theme)

Shortcut: `pip -r requirements-dev.txt` (This also installs the requirements required for running from source)

For more information about contributing to this project, please see the contribution section [below](#contributing)

## Running

### Command-line
To run the program in command line mode, run the following command in your operating system's console:
`Amulet_Map_Editor --command-line`


## Documentation

### Building the Documentation
To build the documentation locally, run the following command: `make html` and then navigate to the
generated directory `docs_build/html` in your favorite web browser


## Contributing

### Running from Source
1. Clone the project using `git clone https://github.com/Podshot/Amulet-Map-Editor`
2. When inside the folder you cloned, install the requirements using `pip -r requirements.txt`
3. To format your files automatically before committing changes, use `pre-commit install`

### Branch Naming
Branches should be created when a certain bug or feature may take multiple attempts to fix. Naming
them should follow the following convention (even for forked repositories when a pull request is being made):

* For features, use: `impl-<feature name>`
* For bug fixes, use: `bug-<bug tracker ID>`
* For improvements/rewrites, use: `improv-<feature name>`

### Code Formatting
For code formatting, we use the formatting utility [black](https://github.com/ambv/black). To run
it on a file, run the following command from your favorite terminal after installing: `black <path to file>`

While formatting is not strictly required for each commit, we ask that after you've finished your
code changes for your Pull Request to run it on every changed file.

### Pull Requests
We ask that submitted Pull Requests give moderately detailed notes about the changes and explain 
any changes that were made to the program outside of those directly related to the feature/bug-fix.
Please make sure to run all tests and include a written verification that all tests have passed.

_Note: We will also re-run all tests before reviewing, this is to mitigate additional changes/commits
needed to pass all tests._

Once a Pull Request is submitted, we will mark the request for review, once that is done, we will
review the changes and provide any notes/things to change. Once all additional changes have been made,
we will merge the request.


## License
This software is available under the MIT license.