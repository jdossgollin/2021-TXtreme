# jdossgollin/2021-TXtreme

Welcome to the code repository for the paper "[How unprecedented was the February 2021 Texas cold snap?](https://doi.org/10.1088/1748-9326/ac0278)" by [James Doss-Gollin](https://dossgollin-lab.github.io/) (Rice), [David J. Farnham](https://www.davidjfarnham.com/) (Carnegie Institute for Science), [Upmanu Lall](http://www.columbia.edu/~ula2/) (Columbia), and [Vijay Modi](https://www.me.columbia.edu/faculty/vijay-modi) (Columbia).

Some edits to this repository have been made since the paper was published (to add analysis of summer extremes and to run for more years).
For the exact version used to generate our published results, a permananent repository is available on Zenodo [![DOI](https://zenodo.org/badge/339750007.svg)](https://zenodo.org/badge/latestdoi/339750007).

## How to cite

This paper is available **OPEN ACCESS** in the journal Environmental Research Letters.
To cite our results and/or methods, please cite it as something like:

```bibtex
@article{doss-gollin_txtreme:2021,
  title = {How Unprecedented Was the {{February}} 2021 {{Texas}} Cold Snap?},
  author = {{Doss-Gollin}, James and Farnham, David J. and Lall, Upmanu and Modi, Vijay},
  year = {2021},
  issn = {1748-9326},
  doi = {10.1088/1748-9326/ac0278},
  journal = {Environmental Research Letters},
}
```

Several summaries of this work are available.
If you'd like a high-level overview of this work, we suggest this [Twitter thread](https://twitter.com/jdossgollin/status/1395484338750431237) by James Doss-Gollin, a [summary](https://cee.rice.edu/news/was-februarys-winter-storm-texas-unprecedented) by Rice University, or a Columbia Earth Institute [blog post](https://blogs.ei.columbia.edu/2021/03/16/unprecedented-texas-cold-snap/) by all authors.
You can also view the poster summarizing this work included [in this repository](./doc/agu21/poster.pdf).

## For researchers

We strive to make our work accessible to an inquiring public and to the scientific community.
Thus we use only publicly available data sets.
All code is posted on this repository.

The following sections outline the steps you can take to examine and reproduce our work.

### Repository organization

- `LICENSE` describes the terms of the GNU GENERAL PUBLIC LICENSE under which our code is licensed. This is a "free, copyleft license".
- `README.md` is what you are looking at
- `Snakefile` implements our workflow. From the Snakemake [documentation](snakemake.readthedocs.io/): "The Snakemake workflow management system is a tool to create reproducible and scalable data analyses. Workflows are described via a human readable, Python based language."
- `codebase/` provides a Python package that various scripts use. Modules are provided to read the GHCN data (`read_ghcn`), to keep track of the directory path structure (`path`), to parse the input data sources (`data`), to perform common calculations (`calc`), and to add features for interacting with figures (`fig`)
- `data/` contains only raw inputs, stored in `data/raw`. If you reproduce our codes (see instructions below), approximately **60 GB** of data will be downloaded to `data/processed.
- `doc/` contains latex files for our paper submissions. You shouldn't need to compile these because [our paper](https://doi.org/10.1088/1748-9326/ac0278) is available open access, but you're welcome to browse. One useful thing you might do here is to identify which figure (in `fig/`) is used in the text!
- `environment.yml` specifies the conda environment used. This should be sufficient to install all required packages for reproducibility. In case you run into issues, `conda.txt` specifies the exact versions of all packages used.
- `fig/` contains final versions of all our figures in both vector graphic (`.pdf`) and image (`.jpg`) formats. All are generated by our source code except for `EGOVA.pdf`, which is generated from the EGOVA [tool](https://bit.ly/EGOVA) produced by Edgar Virgüez. **If you want to use these figures, you are responsible for complying with the policies of Environmental Research Letters**, but we mainly ask that you cite our paper when you do so.
- `scripts/` contains the python scripts used to get and parse raw data, process data, and produce outputs. All figures are produced within Jupyter notebooks; they are the last step of the analysis. Please note that many scripts import modules from `codebase`, the internal package described above.
- `setup.py` makes `codebase` available for installation

### To browse the codes

> If you want to browse our code, this section is for you.

You will find four Jupyter notebooks in `scripts/`.
You can open them and they will render in GitHub.
This will show you how we produced all figures in our paper, along with some additional commentary.

If you want to dig deeper, but not to run our codes, then you may want to look at the Python scripts in `scripts/` and/or the module in `codebase/`.

### To run the codes

> If you want to reproduce or modify our results, this section is for you

Please note: **running this will require approximately 60GB of disk space**.
_All commands here assume standard UNIX terminal; Windows may be subtly different_.

First, `git clone` the repository to your machine.

Next, you will need to install conda (we recommend miniconda) and `wget`.

Next, you need to create th conda environment:

```shell
conda env create --file environment.yml
```

_If this gives you any trouble, you can use the exact version of packages that we did (this worked on an Apple M1 Macbook emulating OSX-64 but your mileage may vary on other systems):_

```shell
conda create --name txtreme --file conda.txt
```

Once you have created the environment, then activate it:

```shell
conda activate txtreme
```

You will also need to install our custom module in `codebase`

```shell
pip install -e .
```

In order to run, you will need to do two things to access required data.

1. Download the GPWV4 data. See instructions in [`data/raw/gpwv4/README.md`](data/raw/gpwv4/README.md).
1. Register for [a CDSAPI key](https://cds.climate.copernicus.eu/api-how-to) with the ECMWF. This key is **required** for you to access this data. If you do not properly install the CDSAPI key, you will not be able to download the ERA-5 reanalysis data.

Now you can run!

```shell
snakemake --n <some number>
```

where `<some number>` specifies the number of cores to use (if you have no idea what this means, try 3: `snakemake --n 3`.
We again remind you that running will use nearly 60GB of disk space; a fast internet connection will be helpful.

## Issues and comments

- If you have issues related to the software, please raise an issue in the Issues tab.
- If you have comments, please contact the corresponding author, [James Doss-Gollin](https://jdossgollin.github.io), directly
