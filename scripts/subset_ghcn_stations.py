"""
Filter the GHCND stations
"""

import argparse
import os
from tqdm import tqdm

import pandas as pd

from src.read_ghcn import read_ghcn_data_file
from src.path import PARDIR

STATES = ["TX"]
MIN_OBS = 60 * 365.25

COLNAMES = [
    "ID",
    "LATITUDE",
    "LONGITUDE",
    "ELEVATION",
    "STATE",
    "NAME",
    "GSN FLAG",
    "HCN_CRN_FLAG",
    "WMO_ID",
]
COLSPECS = [
    (0, 11),
    (12, 20),
    (21, 30),
    (31, 37),
    (38, 40),
    (41, 71),
    (72, 75),
    (76, 79),
    (80, 85),
]


def is_valid_record(stnid: str) -> bool:
    """Does an ID have sufficient data?"""
    fname = os.path.join(PARDIR, "data", "raw", "ghcnd_all", f"{stnid}.dly")
    dat = read_ghcn_data_file(fname, variables=["TMIN", "TMAX"])
    return (dat.shape[0] >= MIN_OBS) & (dat.index.max().year == 2021)


def main() -> None:
    """Run everything"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile", type=str)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    assert args.outfile, "please specify outfile file"
    assert args.infile, "please specify input file"

    # read in all stations & get only those in STATES
    stations = pd.read_fwf(args.infile, names=COLNAMES, colspecs=COLSPECS).loc[
        lambda df: df["STATE"].isin(STATES),
        ["ID", "LATITUDE", "LONGITUDE", "STATE", "NAME"],
    ]

    # get the IDs that have sufficient data
    valid_ids = [stnid for stnid in tqdm(stations["ID"]) if is_valid_record(stnid)]

    # save the valid stations
    valid_stations = stations.loc[lambda df: df["ID"].isin(valid_ids)]
    valid_stations.to_csv(args.outfile, index=False)


if __name__ == "__main__":
    main()
