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

    ecmwf_client = cdsapi.Client()
    ecmwf_client.retrieve(
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
                "01:00",
                "02:00",
                "03:00",
                "04:00",
                "05:00",
                "06:00",
                "07:00",
                "08:00",
                "09:00",
                "10:00",
                "11:00",
                "12:00",
                "13:00",
                "14:00",
                "15:00",
                "16:00",
                "17:00",
                "18:00",
                "19:00",
                "20:00",
                "21:00",
                "22:00",
                "23:00",
            ],
            "area": [38, -108, 25, -92],
            "format": "netcdf",
        },
        args.outfile,
    )


if __name__ == "__main__":
    main()
