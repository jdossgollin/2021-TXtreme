# 2021-TXtreme

<a href="https://eartharxiv.org/repository/view/2122/">
<img src="https://img.shields.io/static/v1?label=&message=Preprint&color=purple&logo=arxiv&style=flat" alt="Link">
</a>

[![DOI](https://zenodo.org/badge/339750007.svg)](https://zenodo.org/badge/latestdoi/339750007)

Welcome to the code repository for the paper "How unprecedented was the February 2021 Texas cold snap?" by [James Doss-Gollin](https://dossgollin-lab.github.io/) (Rice), [David J. Farnham](https://www.davidjfarnham.com/) (Carnegie Institute for Science), [Upmanu Lall](http://www.columbia.edu/~ula2/) (Columbia), and [Vijay Modi](https://www.me.columbia.edu/faculty/vijay-modi) (Columbia)

This paper is available **OPEN ACCESS** in the journal Environmental Research Letters.
Please cite it as something like:

```bibtex
@article{doss-gollin_txtreme:2021,
  title = {How Unprecedented Was the {{February}} 2021 {{Texas}} Cold Snap?},
  author = {Doss-Gollin, James and Farnham, David J. and Lall, Upmanu and Modi, Vijay},
  date = {2021},
  journaltitle = {Environmental Research Letters},
  shortjournal = {Environ. Res. Lett.},
  issn = {1748-9326},
  doi = {10.1088/1748-9326/ac0278},
  langid = {english},
}
```

## Reproducibility

We strive to make our work accessible to an inquiring public and to the scientific community.
Thus we use only publicly available data sets.
All code is posted on this repository.

### To Examine

> If you want to browse our code, this section is for you.

You will find four Jupyter notebooks in `scripts/`.
You can open them and they will render in GitHub.
This will show you figures in our paper with some additional commentary.

### To dig deep

> Our Jupyter notebooks use outputs from other scripts to create visualizations.
> If you want to dig into those scripts, this section is for you.

We use [Snakemake](snakemake.readthedocs.io/) to organize or code.
The `Snakefile` organizes all inputs and provides comments.
Some commands in the `Snakefile` use `wget` to access data.
All others run python scripts with command line arguments.
You will find these scripts in `scripts/`.

Some functions are called across more than one script.
To provide consistency, shared functions are placed in `scripts/codebase`.

### To Run

> If you want to run or modify our results, this section is for you.

Please note: **running this will require approximately 60GB of disk space**.
You have been warned!
*All commands here assume standard UNIX terminal; Windows may be subtly different*.

First, `git clone` the repository to your machine.

Next, you will need to install conda (we recommend miniconda) and `wget`.

Next, you need to create th conda environment:

```shell
conda env create --file environment.yml
```

If this gives you any trouble, you can see the exact versions of packages we used in `conda.txt`.
Once you have created the environment, then

```shell
conda activate txtreme
```

to activate it.
You will also need to install our helper functions

```shell
pip install -e .
```

In order to run, you will need to do two things to access required data.

1. Download the GPWV4 data. See instructions in [`data/raw/gpwv4/README.md`](data/raw/gpwv4/README.md).
1. Register for [a CDSAPI key](https://cds.climate.copernicus.eu/api-how-to) with the ECMWF. This key is required for you to access this data.

Now you can run!

```shell
snakemake --n <some number>
```

where `<some number>` specifies the number of cores to use.
More cores will run faster.
Again, note that running will use nearly 60GB of disk space!
