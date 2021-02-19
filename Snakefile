import numpy as np

BERKELEY_DECADES = np.arange(1880, 2020, 10)

rule default_rule:
    input: 
        "data/processed/ghcnd_valid.csv",
        expand("data/processed/berkeleyearth/{var}.nc", var=["TMIN", "TMAX", "TAVG"]),
        "data/processed/era5/temperature.nc",

# Download the raw berkeley earth temperature data: http://berkeleyearth.org/data/
rule get_berkeley_earth:
    output: "data/raw/berkeleyearth/{var}_{decade}.nc"
    shell: "wget -O {output} http://berkeleyearth.lbl.gov/auto/Global/Gridded/Complete_{wildcards.var}_Daily_LatLong1_{wildcards.decade}.nc"

rule aggregate_berkeley_earth:
    input: 
        script = "scripts/aggregate_berkeleyearth.py",
        files = expand("data/raw/berkeleyearth/{{var}}_{decade}.nc", decade=BERKELEY_DECADES),
    output: "data/processed/berkeleyearth/{var}.nc"
    shell: "python {input.script} -i {input.files} -o {output}"

rule get_era5:
    input: script="scripts/get_era5.py"
    output: "data/processed/era5/temperature.nc"
    shell: "python {input.script} -o {output}"

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
        dat = "data/raw/ghcnd_all/{stnid}.dly",
    output: "data/processed/exceedances/{stnid}.csv"
    shell: "python {input.script} --stnid {stnid} -o {output}"
