"""
Calculate the empirical return period of cold temperature extremes for a given GNCH station
"""

import argparse
from tqdm import tqdm

import numpy as np
import pandas as pd

from codebase.calc import cold_return_period
from codebase.data import get_ghcn_data

DURATIONS = [1, 2, 3, 4]


def calc_return_period(stnid: str) -> pd.Series:
    """
    Calculate the probability with which the 2020-21 winter is exceeded in
    the historical record using an empirical estimator
    """

    temp = (
        get_ghcn_data(stnid)
        .assign(TAVG=lambda df: (df["TMAX"] + df["TMIN"] / 2))
        .dropna()
    )

    # get rolling minima
    temp_roll = pd.DataFrame(
        {f"temp_{dur}_days": temp["TAVG"].rolling(dur).mean() for dur in DURATIONS}
    ).dropna()

    # define years starting in the summer so winter seasons are grouped together
    temp_roll["winter_season"] = temp_roll.index.year + np.int_(
        temp_roll.index.month > 7
    )
    temp_annual = temp_roll.groupby("winter_season").min().dropna()

    temp_hist = temp_annual.loc[0:2020, :]
    temp_21 = temp_annual.loc[2021]

    exceedance = pd.DataFrame(
        {"stnid": [stnid]},
    ).set_index("stnid")

    for dur in DURATIONS:
        col = f"temp_{dur}_days"
        exceedance[col] = cold_return_period(temp_21[col], temp_hist[col])
        was_record = temp_21[col] < temp_hist[col].min()
        exceedance[f"record_{dur}_days"] = was_record

    return exceedance


def main() -> None:
    """Run everything"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile", type=str)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    stations = pd.read_csv(args.infile)["ID"].unique()
    exceedance_probs = pd.concat(
        [calc_return_period(stnid) for stnid in tqdm(stations)], axis=0
    )
    exceedance_probs.to_csv(args.outfile)


if __name__ == "__main__":
    main()
