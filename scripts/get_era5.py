"""
Download
"""

import argparse

import cdsapi
import numpy as np


def main() -> None:
    """Run everything"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    client = cdsapi.Client()
    client.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": "2m_temperature",
            "year": [f"{yr}" for yr in np.arange(1979, 2021 + 1)],
            "month": [
                "01",
                "02",
                "12",
            ],
            "day": [f"{day}" for day in np.arange(1, 31 + 1)],
            "time": [
                "00:00",
                "06:00",
                "12:00",
                "18:00",
            ],
            "area": [
                38,
                -108,
                25,
                -92,
            ],
            "format": "netcdf",
        },
        args.outfile,
    )


if __name__ == "__main__":
    main()