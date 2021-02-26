"""
Compute minimum, maximum, mean, and anomaly (of mean) daily summaries of
temperature from ERA5
"""

import argparse

from pandas import Timedelta
import xarray as xr

CLIMATOLOGY_SDATE = "1979-12-31"
CLIMATOLOGY_EDATE = "2020-02-28"
TIME_ZONE_OFFSET = 6  # group by 1 day in Texas, not UTC


def calculate_anomaly(da, groupby_type="time.month"):
    """From Xarray docs"""
    clim = (
        da.sel(time=slice(CLIMATOLOGY_SDATE, CLIMATOLOGY_EDATE))
        .groupby(groupby_type)
        .mean(dim="time")
    )
    return da.groupby(groupby_type) - clim


def main() -> None:
    """Run the analysis"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infiles", nargs="+", type=str)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    temp = xr.open_mfdataset(args.infiles)["t2m"]

    # combine the two experiments
    # see https://confluence.ecmwf.int/pages/viewpage.action?pageId=173385064
    if "expver" in temp.dims:
        temp = temp.mean(dim="expver")

    # adjust time
    temp["time"] = temp["time"] + Timedelta(TIME_ZONE_OFFSET, unit="H")

    # convert Kelvin to F
    temp = (temp - 273) * 9 / 5 + 32

    # force Dask to compute
    temp = temp.compute()

    # calculate daily climatology and anomalies
    daily_anomaly = calculate_anomaly(
        temp.resample(time="1D").mean(), groupby_type="time.month"
    )

    # save *daily* data
    xr.Dataset(
        {
            "tmin": temp.resample(time="1D").min(),
            "tmax": temp.resample(time="1D").max(),
            "tavg": temp.resample(time="1D").mean(),
            "anomaly": daily_anomaly,
        }
    ).to_netcdf(args.outfile, format="NETCDF4")


if __name__ == "__main__":
    main()
