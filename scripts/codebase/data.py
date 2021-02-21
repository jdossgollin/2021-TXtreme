"""
Functions to read and parse temperature data from three sources:

1. Berkeley Earth
2. ERA5 Reanalysis
3. GHCN Stations
"""

import os

import pandas as pd
import xarray as xr

from .read_ghcn import read_ghcn_data_file

PARDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


def get_berkeley_earth() -> xr.Dataset:
    """Get the Berkeley Earth data"""
    temp = xr.Dataset(
        dict(
            tmax=xr.open_dataarray(
                os.path.join(PARDIR, "data", "processed", "berkeleyearth", "TMAX.nc")
            ),
            tmin=xr.open_dataarray(
                os.path.join(PARDIR, "data", "processed", "berkeleyearth", "TMIN.nc")
            ),
            tavg=xr.open_dataarray(
                os.path.join(PARDIR, "data", "processed", "berkeleyearth", "TAVG.nc")
            ),
        )
    )
    return temp * 9 / 5 + 32  # degrees F


def get_ghcn_data(stnid: str) -> pd.DataFrame:
    """Get the GHCN data for a particular file"""
    fname = os.path.join(PARDIR, "data", "raw", "ghcnd_all", f"{stnid}.dly")
    data = read_ghcn_data_file(fname, variables=["TMIN", "TMAX"]).apply(pd.to_numeric)
    if len(data.columns) >= 2:
        data = data.loc[lambda df: df["TMAX"] > df["TMIN"]]  # otherwise NOT credible
    return data * 9 / 5 / 10 + 32.0  # to degrees F
