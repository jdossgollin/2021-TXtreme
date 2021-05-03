"""
Calculate local return periods of cold weather using the ERA5 data
"""

import argparse
from tqdm import tqdm

import numpy as np
import pandas as pd
import xarray as xr

from codebase.calc import cold_return_period

BASE_TEMP = 65
DURATIONS = [6, 24, 48, 96]


def main() -> None:
    """Run the analysis"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infiles", nargs="+", type=str)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    temp = xr.open_mfdataset(args.infiles)["t2m"].compute()
    temp_roll = xr.concat(
        [
            temp.rolling(time=dur).mean().assign_coords({"duration": dur})
            for dur in DURATIONS
        ],
        dim="duration",
    )

    # group together December YYYY and Jan YYYY+1
    times = pd.to_datetime(temp_roll["time"].values)
    year_eff = times.year + np.int_(times.month > 7)
    temp_roll["year_eff"] = xr.DataArray(
        year_eff, coords={"time": temp_roll["time"]}, dims="time"
    )

    # get annual minimum temperatures
    annual = temp_roll.groupby("year_eff").min(dim="time")

    # computer return periods
    # there may be a better way to do this, but this works
    era5_return = annual.sel(year_eff=2021).copy() * 0
    for lon in tqdm(era5_return["longitude"].values):
        for lat in era5_return["latitude"].values:
            for duration in era5_return["duration"].values:
                sub = annual.sel(longitude=lon, latitude=lat, duration=duration)
                hdd_obs = sub.sel(year_eff=slice(0, 2020)).values
                hdd_21 = sub.sel(year_eff=2021).values
                rt_estimate = cold_return_period(hdd_21, hdd_obs)
                era5_return.loc[
                    dict(longitude=lon, latitude=lat, duration=duration)
                ] = rt_estimate

    era5_return.to_netcdf(args.outfile, format="NETCDF4")


if __name__ == "__main__":
    main()
