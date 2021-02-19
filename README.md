# 2021-texas-extreme-temp

How extreme was the cold snap in Texas?

## Installation

1. `git clone` the repository
1. Install conda
1. `conda env create --file environment.yml` (for dramatic performance improvements you may replace `conda` with [`mamba`](https://github.com/mamba-org/mamba))
1. `conda activate txtreme`

## To Run

1. Download the GPWV4 data
1. Register for [a CDSAPI key](https://cds.climate.copernicus.eu/api-how-to) with the ECMWF

`snakemake --n <some number>`; at least 2 is advised
