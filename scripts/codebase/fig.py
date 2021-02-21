"""Save figures"""

import os

from .data import PARDIR

FIGDIR = os.path.join(PARDIR, "fig")


def figname(name: str) -> str:
    """Get the path to figures"""
    if not os.path.isdir(FIGDIR):
        os.makedirs(FIGDIR)
    return os.path.join(FIGDIR, name)
