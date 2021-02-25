"""
Filter the GHCND stations
"""

import argparse
from tqdm import tqdm

from pandas import to_datetime

from codebase.read_ghcn import read_station_metadata
from codebase.data import get_ghcn_data

STATES = ["TX"]
MIN_OBS = 60 * 365.25
MIN_DATE = "2021-02-17"  # if stations don't have this data, there's no point

# only keep stations that have major cold snaps well recorded
REQUIRED_DATES = [
    "1983-12-23",
    "1983-12-24",
    "1983-12-25",
    "1989-12-12",
    "1989-12-16",
    "1989-12-23",
    "1989-12-24",
    "2011-02-01",
    "2011-02-02",
    "2011-02-03",
    "2011-02-04",
    "2011-02-05",
    "2021-02-15",
    "2021-02-16",
    "2021-02-17",
    "2021-02-18",
    "2021-02-19",
]


def is_valid_record(stnid: str) -> bool:
    """Does an ID have sufficient data?"""
    dat = get_ghcn_data(stnid).dropna()
    conditions = [
        dat.shape[0] >= MIN_OBS,
        dat.index.max() >= to_datetime(MIN_DATE),
        dat.index.isin(REQUIRED_DATES).sum() == len(REQUIRED_DATES),
    ]
    return all(conditions)


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
    stations = (
        read_station_metadata(args.infile)
        .loc[lambda df: df["STATE"].isin(STATES)]
        .reset_index()[["ID", "LATITUDE", "LONGITUDE", "STATE", "NAME"]]
    )

    # get the IDs that have sufficient data
    valid_ids = [stnid for stnid in tqdm(stations["ID"]) if is_valid_record(stnid)]

    # count the number of obs in each
    n_obs = [get_ghcn_data(stnid).dropna().shape[0] for stnid in valid_ids]

    # save the valid stations
    valid_stations = stations.loc[lambda df: df["ID"].isin(valid_ids)]
    valid_stations["n_obs"] = n_obs
    valid_stations.to_csv(args.outfile, index=False)


if __name__ == "__main__":
    main()
