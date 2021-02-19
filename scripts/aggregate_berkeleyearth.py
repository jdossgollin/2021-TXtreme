"""
Aggregate the Berkeley Earth Temperature data
"""

import argparse

import numpy as np
import pandas as pd
import xarray as xr


def parse_file(fname: str) -> xr.Dataset:
    """Read in one of the data files"""
    ds = xr.open_dataset(fname).sel(latitude=slice(25, 50), longitude=slice(-125, -65))
    ds["time"] = pd.to_datetime(ds[["year", "month", "day"]].to_dataframe())
    climatology = (
        ds["climatology"]
        .sel(day_number=np.int_(ds["day_of_year"] - 1))
        .rename({"day_number": "time"})
    )
    climatology["time"] = ds["time"]
    return ds["temperature"] + climatology


def main() -> None:
    """Run everything"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infiles", nargs="+", type=str)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    xr.concat([parse_file(fname) for fname in args.infiles], dim="time").to_netcdf(
        args.outfile, format="NETCDF4"
    )


if __name__ == "__main__":
    main()
