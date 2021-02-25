"""
Snakefile: see snakemake.readthedocs.io/

We use Snakefile to collect required data. Then we run final analysis
steps in Jupyter
"""


import numpy as np

BERKELEY_DECADES = np.arange(1880, 2020, 10)
ERA_YEARS = np.arange(1950, 2022)

# this rule tells Snakemake to create all the data that is imported directly into
# the Jupyter notebooks
rule default_rule:
    input: 
        "data/processed/era5/conus/daily_summaries.nc", 
        "data/processed/era5/tx/daily_summaries.nc",
        "data/processed/era5/tx/pop_hdd.nc",
        "data/processed/era5/tx/hdd_ercot.nc",
        "data/processed/ghcnd/return_periods.csv",
        "data/processed/era5/tx_return_period.nc",
        "data/processed/berkeleyearth/hdd.nc",
        "data/processed/berkeleyearth/TAVG.nc",
        "data/raw/eia/november_generator2020.xlsx",

# use the API to download hourly ERA5 temperature data over Texas
# you will get an error unless you register for account; see README.md
rule get_era5_tx_hourly:
    input: script="scripts/era5_get_tx_hourly.py"
    output: "data/raw/era5/tx/temp_hourly_{year}.nc"
    shell: "python {input.script} --year {wildcards.year} -o {output}"

# use the API to download daily ERA5 temperature data over CONUS
rule get_era5_conus_hourly:
    input: script="scripts/era5_get_conus_hourly.py"
    output: "data/raw/era5/conus/temp_hourly_{year}.nc"
    shell: "python {input.script} --year {wildcards.year} -o {output}"

# compute anomalies of temperature and heating degree days over CONUS for ERA5 data
rule era5_conus_anomalies:
    input:
        script="scripts/era5_daily_summaries.py",
        infiles=expand("data/raw/era5/conus/temp_hourly_{year}.nc", year=ERA_YEARS),
    output: "data/processed/era5/conus/daily_summaries.nc"
    shell: "python {input.script} -i {input.infiles} -o {output}"

# compute anomalies of temperature and heating degree days over TX for ERA5 data
rule era5_tx_anomalies:
    input:
        script="scripts/era5_daily_summaries.py",
        infiles=expand("data/raw/era5/tx/temp_hourly_{year}.nc", year=ERA_YEARS),
    output: "data/processed/era5/tx/daily_summaries.nc"
    shell: "python {input.script} -i {input.infiles} -o {output}"

# compute heating degree days, both multiplied by population density and unweighted
rule era5_tx_hdd:
    input:
        script="scripts/era5_hdd.py",
        temperature=expand("data/raw/era5/tx/temp_hourly_{year}.nc", year=ERA_YEARS),
        population="data/raw/gpwv4/gpw_v4_population_density_rev11_2pt5_min.nc"
    output: "data/processed/era5/tx/pop_hdd.nc"
    shell: "python {input.script} --population {input.population} --temperature {input.temperature} -o {output}"

# aggregate heating degree days over ERCOT
rule hdd_ercot:
    input:
        script="scripts/hdd_ercot.py",
        interconnect="data/raw/interconnects/TexasInterconnect.shp",
        hdd="data/processed/era5/tx/pop_hdd.nc"
    output: "data/processed/era5/tx/hdd_ercot.nc"
    shell: "python {input.script} --boundary {input.interconnect} --hdd {input.hdd} -o {output}"

# estimate grid cell by grid cell lagged return periods using the ERA5 data
rule era5_return:
    input:
        script="scripts/era5_return.py",
        infiles = expand("data/raw/era5/tx/temp_hourly_{year}.nc", year=ERA_YEARS),
    output: "data/processed/era5/tx_return_period.nc"
    shell: "python {input.script} -i {input.infiles} -o {output}"

# Download the raw berkeley earth temperature data
rule get_berkeley_earth:
    output: "data/raw/berkeleyearth/{var}_{decade}.nc"
    shell: "wget -O {output} http://berkeleyearth.lbl.gov/auto/Global/Gridded/Complete_{wildcards.var}_Daily_LatLong1_{wildcards.decade}.nc"

# aggregate berkeley earth data
rule berkeley_earth_aggregate:
    input: 
        script = "scripts/berkeley_earth_aggregate.py",
        files = expand("data/raw/berkeleyearth/{{var}}_{decade}.nc", decade=BERKELEY_DECADES),
    output: "data/processed/berkeleyearth/{var}.nc"
    shell: "python {input.script} -i {input.files} -o {output}"

# convert berkeley earth data to daily heating degree days (degrees F)
rule berkeley_earth_hdd:
    input:
        script = "scripts/berkeley_earth_hdd.py",
        tmin = "data/processed/berkeleyearth/TMIN.nc",
        tmax = "data/processed/berkeleyearth/TMAX.nc",
    output: "data/processed/berkeleyearth/hdd.nc"
    shell: "python {input.script} --tmin {input.tmin} --tmax {input.tmax} -o {output}"

# Download the list of all GHCND stations and metadata from NOAA
rule get_ghcnd_stations:
    output: "data/raw/ghcnd_stations.txt"
    shell: "wget -O {output} https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"

# Download and unzip the GHCND data from NOAA
rule get_ghcnd_data:
    output: "data/raw/ghcnd_all/USW00012960.dly"
    shell: "wget https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_all.tar.gz -O - | tar -xz -C data/raw"

# get only GHCN stations that are in Texas and have sufficient useful data (see script for details)
rule ghcn_subset:
    input:
        "data/raw/ghcnd_all/USW00012960.dly", # an example file to force it to run
        script = "scripts/ghcn_subset.py",
        stations = "data/raw/ghcnd_stations.txt",
    output: "data/processed/ghnd/valid_stations.csv"
    shell: "python {input.script} -i {input.stations} -o {output}"

# calculate exceedance probabilities from GHCN data
rule historical_exceedance:
    input:
        script = "scripts/ghcn_return_period.py",
        stations = "data/processed/ghnd/valid_stations.csv",
    output: "data/processed/ghcnd/return_periods.csv"
    shell: "python {input.script} -i {input.stations} -o {output}"

# US EIA Preliminary Monthly Electric Generator Inventory (based on Form EIA-860M as a supplement to Form EIA-860)
rule eia_data:
    output: "data/raw/eia/november_generator2020.xlsx"
    shell: "wget -O {output} https://www.eia.gov/electricity/data/eia860m/xls/november_generator2020.xlsx"
