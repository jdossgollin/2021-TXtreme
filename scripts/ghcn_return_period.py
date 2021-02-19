"""
Calculate the empirical return period of cold temperature extremes for a given GNCH station
"""

import argparse
import os

import numpy as np
import pandas as pd

from src.read_ghcn import read_ghcn_data_file
from src.path import PARDIR

BASE_TEMP = 68  # degrees F
DURATIONS = [1, 2, 3, 4, 5, 6]

STNID = "USW00012918"


def calc_hdd(stnid: str, base_temp: int = BASE_TEMP) -> pd.DataFrame:
    """Read the input data file and calculate a time series of heating degree days"""
    fname = os.path.join(PARDIR, "data", "raw", "ghcnd_all", f"{stnid}.dly")
    temp = read_ghcn_data_file(fname, variables=["TMIN", "TMAX"]).apply(
        lambda x: x * 0.9 / 5 + 32  # 0.1 deg C to deg F
    )
    # TAVG has spotty data availability so create a midpoint temperature
    heat_deg_days = base_temp - (temp["TMIN"] + temp["TMAX"]) / 2
    heat_deg_days.loc[lambda df: df < 0] = 0.0
    return heat_deg_days


def calc_historical_exceedance_prob(
    stnid: str, base_temp: int = BASE_TEMP
) -> pd.Series:
    """
    Calculate the probability with which the 2020-21 winter is exceeded in
    the historical record using an empirical estimator
    """
    hdd = calc_hdd(stnid, base_temp=base_temp)
    hdd_roll = pd.DataFrame(
        {f"hdd_{dur}_days": hdd.rolling(dur).mean() for dur in DURATIONS}
    ).dropna()

    # define years starting in the summer so winter seasons are grouped together
    hdd_roll["temp_year"] = hdd_roll.index.year + np.int_(hdd_roll.index.month > 7)
    hdd_annual = hdd_roll.groupby("temp_year").max()

    hdd_2021 = hdd_annual.loc[2021]
    hdd_hist = hdd_annual.loc[:2020]

    return (hdd_hist > hdd_2021).mean()


def main() -> None:
    """Run everything"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--stnid", type=str, default="USW00012918")
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    historical_exceedances = calc_historical_exceedance_prob(args.stnid)
    historical_exceedances.name = args.stnid
    historical_exceedances.to_csv(args.outfile)


if __name__ == "__main__":
    main()
