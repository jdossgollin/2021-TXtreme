"""
Compute minimum, maximum, mean, and anomaly (of mean) daily summaries of
temperature from ERA5
"""

import argparse

import numpy as np
import xarray as xr

BASE_TEMP = 68
GPWV4_YEARS = [2000, 2005, 2010, 2015, 2020]


def main() -> None:
    """Run the analysis"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--temperature", nargs="+", type=str)
    parser.add_argument("--population", type=str)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    # get the temperature data
    temp = xr.open_mfdataset(args.temperature)["t2m"]

    # combine the two experiments
    # see https://confluence.ecmwf.int/pages/viewpage.action?pageId=173385064
    if "expver" in temp.dims:
        temp = temp.mean(dim="expver")

    # convert Kelvin to F
    temp = (temp - 273) * 9 / 5 + 32

    # force Dask to compute
    temp = temp.compute()

    # heating degree days
    heat_deg_days = xr.apply_ufunc(np.maximum, BASE_TEMP - temp, 0)

    # now get the population data
    population_density = (
        xr.open_dataarray(args.population)
        .sel(raster=slice(1, 5))
        .assign_coords(pop_year=("raster", GPWV4_YEARS))
        .drop_vars("raster")
        .rename({"raster": "pop_year"})
        .interp_like(heat_deg_days)  # interpolate onto HDD grid
    )
    population_density["pop_year"] = np.array(GPWV4_YEARS)

    # combine the data sets -- they have the same grid now!
    pop_hdd = population_density * heat_deg_days

    # save weighted and unweighted HDD
    xr.Dataset(
        {
            "hdd_pop_weighted": pop_hdd,
            "hdd_unweighted": heat_deg_days,
        }
    ).to_netcdf(args.outfile, format="NETCDF4")


if __name__ == "__main__":
    main()
