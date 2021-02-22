"""
Get the Berkeley Earth data as
"""

import argparse

import numpy as np
import xarray as xr

BASE_TEMP = 68


def main() -> None:
    """Run the analysis"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--tmin", type=str)
    parser.add_argument("--tmax", type=str)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    t_hdd = (xr.open_dataarray(args.tmin) + xr.open_dataarray(args.tmax)) / 2
    hdd = np.maximum(BASE_TEMP - t_hdd, 0).resample(time="1D").mean()
    hdd.name = "HDD"

    hdd.to_netcdf(args.outfile, format="NETCDF4")


if __name__ == "__main__":
    main()
