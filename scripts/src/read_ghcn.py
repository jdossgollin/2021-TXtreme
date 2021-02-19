"""
File: read_ghcn.py
Author: Ned Haughton (https://gitlab.com/nedcr)
Description: Code for reading GHCN dly file data
Source: https://gitlab.com/snippets/1838910
"""

import pandas as pd


# Metadata specs #

METADATA_COL_SPECS = [
    (0, 12),
    (12, 21),
    (21, 31),
    (31, 38),
    (38, 41),
    (41, 72),
    (72, 76),
    (76, 80),
    (80, 86),
]

METADATA_NAMES = [
    "ID",
    "LATITUDE",
    "LONGITUDE",
    "ELEVATION",
    "STATE",
    "NAME",
    "GSN FLAG",
    "HCN/CRN FLAG",
    "WMO ID",
]

METADATA_DTYPE = {
    "ID": str,
    "STATE": str,
    "NAME": str,
    "GSN FLAG": str,
    "HCN/CRN FLAG": str,
    "WMO ID": str,
}

DATA_HEADER_NAMES = ["ID", "YEAR", "MONTH", "ELEMENT"]

DATA_HEADER_COL_SPECS = [(0, 11), (11, 15), (15, 17), (17, 21)]

DATA_HEADER_DTYPES = {"ID": str, "YEAR": int, "MONTH": int, "ELEMENT": str}

DATA_COL_NAMES = [
    [
        "VALUE" + str(i + 1),
        "MFLAG" + str(i + 1),
        "QFLAG" + str(i + 1),
        "SFLAG" + str(i + 1),
    ]
    for i in range(31)
]
# Join sub-lists
DATA_COL_NAMES = sum(DATA_COL_NAMES, [])

DATA_REPLACEMENT_COL_NAMES = [
    [("VALUE", i + 1), ("MFLAG", i + 1), ("QFLAG", i + 1), ("SFLAG", i + 1)]
    for i in range(31)
]
# Join sub-lists
DATA_REPLACEMENT_COL_NAMES = sum(DATA_REPLACEMENT_COL_NAMES, [])
DATA_REPLACEMENT_COL_NAMES = pd.MultiIndex.from_tuples(
    DATA_REPLACEMENT_COL_NAMES, names=["VAR_TYPE", "DAY"]
)

DATA_COL_SPECS = [
    [
        (21 + i * 8, 26 + i * 8),
        (26 + i * 8, 27 + i * 8),
        (27 + i * 8, 28 + i * 8),
        (28 + i * 8, 29 + i * 8),
    ]
    for i in range(31)
]
DATA_COL_SPECS = sum(DATA_COL_SPECS, [])

DATA_COL_DTYPES = [
    {
        "VALUE" + str(i + 1): int,
        "MFLAG" + str(i + 1): str,
        "QFLAG" + str(i + 1): str,
        "SFLAG" + str(i + 1): str,
    }
    for i in range(31)
]
DATA_HEADER_DTYPES.update({k: v for d in DATA_COL_DTYPES for k, v in d.items()})


def read_station_metadata(filename="ghcnd-stations.txt"):
    """Reads in station metadata

    :filename: ghcnd station metadata file.
    :returns: station metadata as a pandas Dataframe

    """
    return pd.read_fwf(
        filename,
        METADATA_COL_SPECS,
        names=METADATA_NAMES,
        index_col="ID",
        dtype=METADATA_DTYPE,
    )


def read_ghcn_data_file(
    filename="ghcnd_all/ACW00011604.dly",
    variables=None,
    include_flags=False,
    dropna="all",
):
    """Reads in all data from a GHCN .dly data file

    :param filename: path to file
    :param variables: list of variables to include in output dataframe
        e.g. ['TMAX', 'TMIN', 'PRCP']
    :param include_flags: Whether to include data quality flags in the final output
    :returns: Pandas dataframe
    """

    df = pd.read_fwf(
        filename,
        colspecs=DATA_HEADER_COL_SPECS + DATA_COL_SPECS,
        names=DATA_HEADER_NAMES + DATA_COL_NAMES,
        index_col=DATA_HEADER_NAMES,
        dtype=DATA_HEADER_DTYPES,
    )

    if variables is not None:
        df = df[df.index.get_level_values("ELEMENT").isin(variables)]

    df.columns = DATA_REPLACEMENT_COL_NAMES

    if not include_flags:
        df = df.loc[:, ("VALUE", slice(None))]
        df.columns = df.columns.droplevel("VAR_TYPE")

    df = df.stack(level="DAY").unstack(level="ELEMENT")

    if dropna:
        df.replace(-9999.0, pd.NA, inplace=True)
        df.replace(-9999, pd.NA, inplace=True)
        df.dropna(how=dropna, inplace=True)

    df.index = pd.to_datetime(
        df.index.get_level_values("YEAR") * 10000
        + df.index.get_level_values("MONTH") * 100
        + df.index.get_level_values("DAY"),
        format="%Y%m%d",
    )

    return df
