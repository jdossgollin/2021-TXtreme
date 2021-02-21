"""
Get the ERA5 daily heating degree days (degrees F)
"""

import argparse

import numpy as np
import xarray as xr

BASE_TEMP = 68


def main() -> None:
    """Run the analysis"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile", type=str)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    era5 = xr.open_dataset(args.infile)["t2m"]

    # combine the two experiments
    # see https://confluence.ecmwf.int/pages/viewpage.action?pageId=173385064
    switch_time = np.min(np.where(era5.sel(expver=1).isnull())[0])
    era5 = xr.concat(
        [
            era5.sel(expver=1).isel(time=slice(0, switch_time)),
            era5.sel(expver=5).isel(time=slice(switch_time, -1)),
        ],
        dim="time",
    )

    era5 = (era5 - 273) * 9 / 5 + 32  # Kelvin to F

    # heating degree days
    hdd = np.maximum(BASE_TEMP - era5, 0)
    hdd = hdd.resample(time="1D").mean()
    hdd.name = "HDD"
    hdd.to_netcdf(args.outfile, format="NETCDF4")


if __name__ == "__main__":
    main()
