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

    era5 = xr.open_mfdataset(args.infiles)["HDD"].compute()
    rolling = xr.Dataset(
        {f"hdd_{dur}_days": era5.rolling(time=dur).mean() for dur in DURATIONS}
    )

    year_eff = pd.to_datetime(rolling["time"].values).year + np.int_(
        pd.to_datetime(rolling["time"].values).month > 7
    )
    rolling["year_eff"] = xr.DataArray(
        year_eff, coords={"time": rolling["time"]}, dims="time"
    )
    annual = rolling.groupby("year_eff").max(dim="time")

    era5_return = annual.sel(year_eff=2021).copy() * 0
    for lon in tqdm(era5_return["longitude"].values):
        for lat in era5_return["latitude"].values:
            for dur in DURATIONS:
                var = f"hdd_{dur}_days"
                sub = annual[var].sel(longitude=lon, latitude=lat)
                hdd_obs = sub.sel(year_eff=slice(0, 2020)).values
                hdd_21 = sub.sel(year_eff=2021).values
                rt_estimate = return_period(hdd_21, hdd_obs)
                era5_return[var].loc[dict(longitude=lon, latitude=lat)] = rt_estimate

    era5_return.to_netcdf(args.outfile, format="NETCDF4")


if __name__ == "__main__":
    main()
