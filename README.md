# 2021-texas-extreme-temp

How extreme was the cold snap in Texas?

**PRELIMINARY** analysis by

- Dr. James Doss-Gollin, Rice University
- Dr. David J. Farnham, Carnegie Institute for Science
- Dr. Upmanu Lall, Columbia University
- Dr. Vijay Modi, Columbia University

## Summary of Findings

## Reproducibility

We strive to make our work accessible to an inquiring public and to the scientific community.
Thus we use only publicly available data sets.
All code is posted on this repository.

### To Examine

You probably want to start by looking at our code.
All code is in the `scripts` folder.
In that folder you will find another directory called `codebase`.
This is imported by some of the scripts.

### To Run

Installation

1. `git clone` the repository
1. Install conda
1. `conda env create --file environment.yml` (for dramatic performance improvements you may replace `conda` with [`mamba`](https://github.com/mamba-org/mamba))
1. `conda activate txtreme`

## To Run

1. Download the GPWV4 data
1. Register for [a CDSAPI key](https://cds.climate.copernicus.eu/api-how-to) with the ECMWF

`snakemake --n <some number>`; at least 2 is advised
