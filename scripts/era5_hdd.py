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
    if "expver" in era5.dims:
        era5 = era5.mean(dim="expver")

    # convert Kelvin to F
    era5 = (era5 - 273) * 9 / 5 + 32

    # heating degree hours
    heat_deg_hours = xr.apply_ufunc(np.maximum, BASE_TEMP - era5, 0)

    # save *daily* data
    xr.Dataset(
        {
            "HDD": heat_deg_hours.resample(time="1D").mean(),
            "tmin": era5.resample(time="1D").min(),
            "tmax": era5.resample(time="1D").max(),
            "tavg": era5.resample(time="1D").mean(),
        }
    ).to_netcdf(args.outfile, format="NETCDF4")


if __name__ == "__main__":
    main()
