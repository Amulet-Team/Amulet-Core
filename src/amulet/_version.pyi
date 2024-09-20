from _typeshed import Incomplete

def get_keywords():
    """Get the keywords needed to look up the version information."""

class VersioneerConfig:
    """Container for Versioneer configuration parameters."""

def get_config():
    """Create, populate and return the VersioneerConfig() object."""

class NotThisMethod(Exception):
    """Exception raised if a method is not valid for the current scenario."""

LONG_VERSION_PY: Incomplete
HANDLERS: Incomplete

def register_vcs_handler(vcs, method):
    """Decorator to mark a method as the handler for a particular VCS."""

def run_command(
    commands,
    args,
    cwd: Incomplete | None = None,
    verbose: bool = False,
    hide_stderr: bool = False,
    env: Incomplete | None = None,
):
    """Call the given command(s)."""

def versions_from_parentdir(parentdir_prefix, root, verbose):
    """Try to determine the version from the parent directory name.

    Source tarballs conventionally unpack into a directory that includes both
    the project name and a version string. We will also support searching up
    two directory levels for an appropriately named parent directory
    """

def git_get_keywords(versionfile_abs):
    """Extract version information from the given file."""

def git_versions_from_keywords(keywords, tag_prefix, verbose):
    """Get version information from git keywords."""

def git_pieces_from_vcs(tag_prefix, root, verbose, run_command=...):
    """Get version from 'git describe' in the root of the source tree.

    This only gets called if the git-archive 'subst' keywords were *not*
    expanded, and _version.py hasn't already been rewritten with a short
    version string, meaning we're inside a checked out source tree.
    """

def plus_or_dot(pieces):
    """Return a + if we don't already have one, else return a ."""

def render_pep440(pieces):
    """Build up version string, with post-release "local version identifier".

    Our goal: TAG[+DISTANCE.gHEX[.dirty]] . Note that if you
    get a tagged build and then dirty it, you\'ll get TAG+0.gHEX.dirty

    Exceptions:
    1: no tags. git_describe was just HEX. 0+untagged.DISTANCE.gHEX[.dirty]
    """

def render_pep440_pre(pieces):
    """TAG[.post.devDISTANCE] -- No -dirty.

    Exceptions:
    1: no tags. 0.post.devDISTANCE
    """

def render_pep440_post(pieces):
    """TAG[.postDISTANCE[.dev0]+gHEX] .

    The ".dev0" means dirty. Note that .dev0 sorts backwards
    (a dirty tree will appear "older" than the corresponding clean one),
    but you shouldn\'t be releasing software with -dirty anyways.

    Exceptions:
    1: no tags. 0.postDISTANCE[.dev0]
    """

def render_pep440_old(pieces):
    """TAG[.postDISTANCE[.dev0]] .

    The ".dev0" means dirty.

    Eexceptions:
    1: no tags. 0.postDISTANCE[.dev0]
    """

def render_git_describe(pieces):
    """TAG[-DISTANCE-gHEX][-dirty].

    Like 'git describe --tags --dirty --always'.

    Exceptions:
    1: no tags. HEX[-dirty]  (note: no 'g' prefix)
    """

def render_git_describe_long(pieces):
    """TAG-DISTANCE-gHEX[-dirty].

    Like 'git describe --tags --dirty --always -long'.
    The distance/hash is unconditional.

    Exceptions:
    1: no tags. HEX[-dirty]  (note: no 'g' prefix)
    """

def render(pieces, style):
    """Render the given version pieces into the requested style."""

def get_versions():
    """Get version information or return default if unable to do so."""
