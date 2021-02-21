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

    era5 = xr.open_mfdataset(args.infile)["HDD"]
    rolling = xr.Dataset(
        {f"hdd_{dur}_days": era5.rolling(time=dur).mean() for dur in DURATIONS}
    )

    year_eff = pd.to_datetime(rolling["time"].values).year + np.int_(
        pd.to_datetime(rolling["time"].values).month > 7
    )
    rolling["year_eff"] = xr.DataArray(
        year_eff, coords={"time": rolling["time"]}, dims="time"
    )
    annual = rolling.groupby("year_eff").mean(dim="time")

    historical = annual.sel(year_eff=slice(0, 2020))
    extreme = annual.sel(year_eff=2021)

    era5_exceedance = extreme.copy() * np.nan
    for lon in tqdm(era5_exceedance["longitude"].values):
        for lat in era5_exceedance["latitude"].values:
            for dur in DURATIONS:
                y = (
                    extreme[f"hdd_{dur}_days"]
                    .sel(longitude=lon, latitude=lat)
                    .values.flatten()
                )
                x = (
                    historical[f"hdd_{dur}_days"]
                    .sel(longitude=lon, latitude=lat)
                    .values.flatten()
                )
                era5_exceedance[f"hdd_{dur}_days"].sel(
                    longitude=lon, latitude=lat
                ).values = return_period(y, x)

    era5_exceedance.to_netcdf(args.outfile, format="NETCDF4")


if __name__ == "__main__":
    main()
