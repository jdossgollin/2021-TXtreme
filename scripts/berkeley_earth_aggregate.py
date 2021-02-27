"""
Aggregate the Berkeley Earth Temperature data
"""

import argparse

import numpy as np
import pandas as pd
import xarray as xr

from codebase.calc import calculate_anomaly


def parse_file(fname: str) -> xr.Dataset:
    """Read in one of the data files"""

    # step 1: figure out what the underlying temperature value is
    bkds = xr.open_dataset(fname).sel(
        latitude=slice(25, 50), longitude=slice(-125, -65)
    )
    bkds["time"] = pd.to_datetime(bkds[["year", "month", "day"]].to_dataframe())
    climatology_c = (
        bkds["climatology"]
        .sel(day_number=np.int_(bkds["day_of_year"] - 1))
        .rename({"day_number": "time"})
    )
    climatology_c["time"] = bkds["time"]
    anomaly_c = bkds["temperature"]
    temp_c = anomaly_c + climatology_c

    # step 2: re-derive climatology using consistent formulat & calc new anomaly
    anomaly_c2 = calculate_anomaly(temp_c, groupby_type="time.season")

    return xr.Dataset(dict(anomaly_f=anomaly_c2 * 9 / 5, temp_f=temp_c * 9 / 5 + 32))


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
