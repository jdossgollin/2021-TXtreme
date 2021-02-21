import numpy as np

BERKELEY_DECADES = np.arange(1880, 2020, 10)

rule default_rule:
    input: 
        "data/processed/ghcnd_exceedances.csv",
        expand("data/processed/berkeleyearth/{var}.nc", var=["TMIN", "TMAX"]),
        "data/processed/era5/exceedance.nc",

# use the API to download hourly ERA5 temperature data
# you will get an error unless you register for account; see README.md
ERA_YEARS = np.arange(1950, 2021+1)
rule get_era5:
    input: script="scripts/get_era5.py"
    output: "data/processed/era5/temp_hourly_{year}.nc"
    shell: "python {input.script} --year {wildcards.year} -o {output}"

# aggregate ERA5 data to daily heating degree days
rule era5_hdd:
    input:
        script="scripts/era5_hdd.py",
        infile="data/processed/era5/temp_hourly_{year}.nc",
    output: "data/processed/era5/hdd_{year}.nc"
    shell: "python {input.script} -i {input.infile} -o {output}"

rule era5_return:
    input:
        script="scripts/era5_return.py",
        infiles = expand("data/processed/era5/hdd_{year}.nc", year=ERA_YEARS),
    output: "data/processed/era5/exceedance.nc"
    shell: "python {input.script} -i {input.infiles} -o {output}"

# Download the raw berkeley earth temperature data: http://berkeleyearth.org/data/
rule get_berkeley_earth:
    output: "data/raw/berkeleyearth/{var}_{decade}.nc"
    shell: "wget -O {output} http://berkeleyearth.lbl.gov/auto/Global/Gridded/Complete_{wildcards.var}_Daily_LatLong1_{wildcards.decade}.nc"

# aggregate berkeley earth data
rule aggregate_berkeley_earth:
    input: 
        script = "scripts/aggregate_berkeleyearth.py",
        files = expand("data/raw/berkeleyearth/{{var}}_{decade}.nc", decade=BERKELEY_DECADES),
    output: "data/processed/berkeleyearth/{var}.nc"
    shell: "python {input.script} -i {input.files} -o {output}"

# convert berkeley earth data to daily heating degree days
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

# get only GHCN stations that are in Texas and have sufficient useful data
rule ghcnd_subset:
    input:
        "data/raw/ghcnd_all/USW00012960.dly", # an example file to force it to run
        script = "scripts/subset_ghcn_stations.py",
        stations = "data/raw/ghcnd_stations.txt",
    output: "data/processed/ghcnd_valid.csv"
    shell: "python {input.script} -i {input.stations} -o {output}"

# GHCN historical exceedance
rule historical_exceedance:
    input:
        script = "scripts/ghcn_return_period.py",
        stations = "data/processed/ghcnd_valid.csv",
    output: "data/processed/ghcnd_exceedances.csv"
    shell: "python {input.script} -i {input.stations} -o {output}"
