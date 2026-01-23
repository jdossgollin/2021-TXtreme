"""
Make it easy to work with the directory structure

Syntax roughly follows that of DrWatson.jl:
https://juliadynamics.github.io/DrWatson.jl/dev/
"""

import os

# Project root is parent of codebase directory
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIGDIR = os.path.join(_PROJECT_ROOT, "fig")
DATADIR = os.path.join(_PROJECT_ROOT, "data")
SCRIPTDIR = os.path.join(_PROJECT_ROOT, "scripts")


def ensure_dir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)


def datadir(*args):
    """Get the directory of something in data"""
    ensure_dir(DATADIR)
    return os.path.join(DATADIR, *args)


def scriptdir(*args):
    """Get the directory of something in the scripts folder"""
    ensure_dir(SCRIPTDIR)
    return os.path.join(SCRIPTDIR, *args)


def figdir(*args):
    """Get the directory of a figure"""
    ensure_dir(FIGDIR)
    return os.path.join(FIGDIR, *args)
