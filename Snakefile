"""
Snakefile: see snakemake.readthedocs.io/

We use Snakefile to collect and process required data. Then we run final analysis steps in Jupyter.
"""


import numpy as np

from codebase.path import datadir, scriptdir, figdir

BERKELEY_DECADES = np.arange(
    1880, 2020, 10
)  # decades to download for the Berkeley Earth data
ERA_YEARS = np.arange(1940, 2023 + 1)  # years to download for ERA5 data


# this rule tells Snakemake to create all the data that is imported directly into the Jupyter notebooks
rule default_rule:
    input:
        figdir("ERCOT_HDD_IDF_MLE_popweighted.pdf"),
        figdir("ERCOT_HDD_IDF_MLE_unweighted.pdf"),
        figdir("ERCOT_HDD_IDF_plotpos_popweighted.pdf"),
        figdir("ERCOT_HDD_IDF_plotpos_unweighted.pdf"),
        figdir("ERCOT_HDD_blog.pdf"),
        figdir("historic_events_era5.pdf"),
        figdir("historic_events_era5_TX.pdf"),
        figdir("historic_events_bk.pdf"),
        figdir("local_rt_ghcnd.pdf"),
        figdir("local_rt_era5.pdf"),
        figdir("HDD_pop_weighted_ts.pdf"),


################################################################################
############################# GET RAW DATA #####################################
################################################################################


# US EIA Preliminary Monthly Electric Generator Inventory (based on Form EIA-860M as a supplement to Form EIA-860)
rule get_generators:
    output:
        datadir("raw", "eia", "november_generator2020.xlsx"),
    shell:
        "wget -O {output} https://www.eia.gov/electricity/data/eia860m/archive/xls/november_generator2020.xlsx"


# Use the CDAS API to download hourly ERA5 temperature data over Texas; you will get an error unless you register for account. See `README.md`.
rule get_era5_tx_hourly:
    input:
        script=scriptdir("era5_get_tx_hourly.py"),
    output:
        datadir("raw", "era5", "tx", "temp_hourly_{year}.nc"),
    shell:
        "python {input.script} --year {wildcards.year} -o {output}"


# use the API to download daily ERA5 temperature data over CONUS
rule get_era5_conus_hourly:
    input:
        script=scriptdir("era5_get_conus_hourly.py"),
    output:
        datadir("raw", "era5", "conus", "temp_hourly_{year}.nc"),
    shell:
        "python {input.script} --year {wildcards.year} -o {output}"


# Download the raw berkeley earth temperature data
rule get_berkeley_earth:
    output:
        datadir("raw", "berkeleyearth", "{var}_{decade}.nc"),
    shell:
        "wget -O {output} http://berkeleyearth.lbl.gov/auto/Global/Gridded/Complete_{wildcards.var}_Daily_LatLong1_{wildcards.decade}.nc"


# Download the list of all GHCND stations and metadata from NOAA
rule get_ghcnd_stations:
    output:
        datadir("raw", "ghcnd_stations.txt"),
    shell:
        "wget -O {output} https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"


# Download and unzip the GHCND data from NOAA
rule get_ghcnd_data:
    output:
        datadir("raw", "ghcnd_all", "USW00012960.dly"),
    shell:
        "wget https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_all.tar.gz -O - | tar -xz -C data/raw"


################################################################################
############################# PROCESS DATA #####################################
################################################################################


# compute anomalies of temperature and heating degree days over CONUS for ERA5 data
rule era5_conus_anomalies:
    input:
        script=scriptdir("era5_daily_summaries.py"),
        infiles=expand(
            datadir("raw", "era5", "conus", "temp_hourly_{year}.nc"), year=ERA_YEARS
        ),
    output:
        datadir("processed", "era5", "conus", "daily_summaries.nc"),
    shell:
        "python {input.script} -i {input.infiles} -o {output}"


# compute anomalies of temperature and heating degree days over TX for ERA5 data
rule era5_tx_anomalies:
    input:
        script=scriptdir("era5_daily_summaries.py"),
        infiles=expand(
            datadir("raw", "era5", "tx", "temp_hourly_{year}.nc"), year=ERA_YEARS
        ),
    output:
        datadir("processed", "era5", "tx", "daily_summaries.nc"),
    shell:
        "python {input.script} -i {input.infiles} -o {output}"


# compute heating degree days, both multiplied by population density and unweighted
rule era5_tx_hdd:
    input:
        script=scriptdir("era5_hdd.py"),
        temperature=expand(
            datadir("raw", "era5", "tx", "temp_hourly_{year}.nc"), year=ERA_YEARS
        ),
        population=datadir(
            "raw", "gpwv4", "gpw_v4_population_density_rev11_2pt5_min.nc"
        ),
    output:
        datadir("processed", "era5", "tx", "pop_hdd.nc"),
    shell:
        "python {input.script} --population {input.population} --temperature {input.temperature} -o {output}"


# aggregate heating degree days over ERCOT
rule hdd_ercot:
    input:
        script=scriptdir("hdd_ercot.py"),
        interconnect=datadir("raw", "eia", "regions_NERC", "NercRegions_201907.shp"),
        hdd=datadir("processed", "era5", "tx", "pop_hdd.nc"),
    output:
        datadir("processed", "era5", "tx", "hdd_ercot.nc"),
    shell:
        "python {input.script} --boundary {input.interconnect} --hdd {input.hdd} -o {output}"


# estimate grid cell by grid cell lagged return periods using the ERA5 data
rule era5_return:
    input:
        script=scriptdir("era5_return.py"),
        infiles=expand(
            datadir("raw", "era5", "tx", "temp_hourly_{year}.nc"), year=ERA_YEARS
        ),
    output:
        datadir("processed", "era5", "tx", "return_period.nc"),
    shell:
        "python {input.script} -i {input.infiles} -o {output}"


# aggregate berkeley earth data
rule berkeley_earth_aggregate:
    input:
        script=scriptdir("berkeley_earth_aggregate.py"),
        files=expand(
            datadir("raw", "berkeleyearth", "{{var}}_{decade}.nc"),
            decade=BERKELEY_DECADES,
        ),
    output:
        datadir("processed", "berkeleyearth", "{var}.nc"),
    shell:
        "python {input.script} -i {input.files} -o {output}"


# convert berkeley earth data to daily heating degree days (degrees F)
rule berkeley_earth_hdd:
    input:
        script=scriptdir("berkeley_earth_hdd.py"),
        tmin=datadir("processed", "berkeleyearth", "TMIN.nc"),
        tmax=datadir("processed", "berkeleyearth", "TMAX.nc"),
    output:
        datadir("processed", "berkeleyearth", "hdd.nc"),
    shell:
        "python {input.script} --tmin {input.tmin} --tmax {input.tmax} -o {output}"


# get only GHCN stations that are in Texas and have sufficient useful data (see script for details)
rule ghcn_subset:
    input:
        datadir("raw/ghcnd_all/USW00012960.dly"),  # pick one to force it to run when the .dly files are updated
        script=scriptdir("ghcn_subset.py"),
        stations=datadir("raw", "ghcnd_stations.txt"),
    output:
        datadir("processed", "ghcnd", "valid_stations.csv"),
    shell:
        "python {input.script} -i {input.stations} -o {output}"


# calculate exceedance probabilities from GHCN data
rule historical_exceedance:
    input:
        script=scriptdir("ghcn_return_period.py"),
        stations=datadir("processed", "ghcnd", "valid_stations.csv"),
    output:
        datadir("processed", "ghcnd", "return_periods.csv"),
    shell:
        "python {input.script} -i {input.stations} -o {output}"


################################################################################
############################# ANALYZE DATA #####################################
################################################################################


rule hdd_idf:
    input:
        datadir("processed", "era5", "tx", "hdd_ercot.nc"),
    output:
        figdir("ERCOT_HDD_IDF_MLE_popweighted.pdf"),
        figdir("ERCOT_HDD_IDF_MLE_unweighted.pdf"),
        figdir("ERCOT_HDD_IDF_plotpos_popweighted.pdf"),
        figdir("ERCOT_HDD_IDF_plotpos_unweighted.pdf"),
        figdir("ERCOT_HDD_blog.pdf"),
    notebook:
        scriptdir("hdd_idf.ipynb")


rule historic_extremes:
    input:
        datadir("processed", "era5", "conus", "daily_summaries.nc"),
        datadir("processed", "era5", "tx", "daily_summaries.nc"),
        datadir("processed", "berkeleyearth", "TAVG.nc"),
    output:
        figdir("historic_events_era5.pdf"),
        figdir("historic_events_era5_TX.pdf"),
        figdir("historic_events_bk.pdf"),
    notebook:
        scriptdir("historic_extremes.ipynb")


rule local_return_period:
    input:
        datadir("processed", "ghcnd", "return_periods.csv"),
        datadir("raw", "ghcnd_stations.txt"),
        datadir("processed", "era5", "tx", "return_period.nc"),
        datadir("raw", "eia", "november_generator2020.xlsx"),
        datadir("raw", "gpwv4", "gpw_v4_population_density_rev11_2pt5_min.nc"),
        datadir("raw", "eia", "regions_NERC/NercRegions_201907.shp"),
    output:
        figdir("local_rt_ghcnd.pdf"),
        figdir("local_rt_era5.pdf"),
    notebook:
        scriptdir("local_return_period.ipynb")


rule HDD_pop_weighted_ts:
    input:
        datadir("processed", "era5", "tx", "hdd_ercot.nc"),
    output:
        figdir("HDD_pop_weighted_ts.pdf"),
    notebook:
        scriptdir("time_series.ipynb")
