"""Save figures"""

import os
from string import ascii_lowercase as letters

import matplotlib.pyplot as plt

from .data import PARDIR

FIGDIR = os.path.join(PARDIR, "fig")


def smart_save(name: str) -> None:
    """Get the path to figures"""
    if not os.path.isdir(FIGDIR):
        os.makedirs(FIGDIR)

    plt.savefig(os.path.join(FIGDIR, f"{name}.pdf"))
    plt.savefig(os.path.join(FIGDIR, f"{name}.jpg"), dpi=300)


def add_panel_text(
    axes: plt.Axes,
    xloc: float = 0.925,
    yloc: float = 0.95,
    fontsize: float = 16,
    fontweight: str = "bold",
    va: str = "top",
    **kwargs,
) -> None:
    """Add (a) (b) (c) etc to each panel"""
    # add letters
    for i, ax in enumerate(axes.flat):
        ax.text(
            xloc,
            yloc,
            f"({letters[i]})",
            transform=ax.transAxes,
            fontsize=fontsize,
            fontweight=fontweight,
            va=va,
            **kwargs,
        )