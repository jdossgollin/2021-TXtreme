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

    era5 = xr.open_dataset(args.infile).sel(expver=1)["t2m"]
    era5 = (era5 - 273) * 9 / 5 + 32
    hdd = np.maximum(BASE_TEMP - era5, 0).resample(time="1D").mean()
    hdd.name = "HDD"

    hdd.to_netcdf(args.outfile, format="NETCDF4")


if __name__ == "__main__":
    main()
