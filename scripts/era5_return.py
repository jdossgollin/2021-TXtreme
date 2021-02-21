"""
Calculate return periods using ERA5
"""

import argparse
from tqdm import tqdm

import numpy as np
import pandas as pd
import xarray as xr

from codebase.calc import return_period

BASE_TEMP = 68
DURATIONS = [1, 2, 3, 4]


def main() -> None:
    """Run the analysis"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infiles", nargs="+", type=str)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    hdd = xr.open_mfdataset(args.infiles)["HDD"].compute()
    hdd_roll = xr.concat(
        [hdd.rolling(time=dur).mean().assign_coords({"lag": dur}) for dur in DURATIONS],
        dim="lag",
    )

    # group together December YYYY and Jan YYYY+1
    times = pd.to_datetime(hdd_roll["time"].values)
    year_eff = times.year + np.int_(times.month > 7)
    hdd_roll["year_eff"] = xr.DataArray(
        year_eff, coords={"time": hdd_roll["time"]}, dims="time"
    )

    # get ann max heating degree days
    annual = hdd_roll.groupby("year_eff").max(dim="time")

    # computer return periods
    # there may be a better way to do this, but this works
    era5_return = annual.sel(year_eff=2021).copy() * 0
    for lon in tqdm(era5_return["longitude"].values):
        for lat in era5_return["latitude"].values:
            for lag in era5_return["lag"].values:
                sub = annual.sel(longitude=lon, latitude=lat, lag=lag)
                hdd_obs = sub.sel(year_eff=slice(0, 2020)).values
                hdd_21 = sub.sel(year_eff=2021).values
                rt_estimate = return_period(hdd_21, hdd_obs)
                era5_return.loc[
                    dict(longitude=lon, latitude=lat, lag=lag)
                ] = rt_estimate

    era5_return.to_netcdf(args.outfile, format="NETCDF4")


if __name__ == "__main__":
    main()
