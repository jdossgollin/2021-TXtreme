"""
Compute HDD from ECMWF forecast data.

Similar to era5_hdd.py but for forecast data.
Interpolates 3-hourly forecast to hourly, then computes HDD.
"""

import argparse
import numpy as np
import pandas as pd
import xarray as xr

BASE_TEMP = 65
GPWV4_YEARS = [2000, 2005, 2010, 2015, 2020]


def main() -> None:
    """Run the analysis"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--forecast", type=str, required=True)
    parser.add_argument("--population", type=str, required=True)
    parser.add_argument("-o", "--outfile", type=str, required=True)
    args = parser.parse_args()

    # Load forecast data
    print(f"Loading forecast from {args.forecast}")
    ds_fcst = xr.open_dataset(args.forecast)

    # Get temperature in Fahrenheit
    if "t2m_f" in ds_fcst:
        temp = ds_fcst["t2m_f"]
    else:
        # Convert from Kelvin if needed
        temp_var = "t2m" if "t2m" in ds_fcst else "2t"
        temp = (ds_fcst[temp_var] - 273.15) * 9/5 + 32

    # Interpolate to hourly (forecast is 3-hourly)
    time_dim = "time" if "time" in temp.dims else "step"

    # If using 'step' (forecast lead time), convert to absolute time
    if time_dim == "step":
        # Get initialization time from coordinates
        if "time" in ds_fcst.coords:
            init_time = pd.Timestamp(ds_fcst["time"].values)
        else:
            raise ValueError("Cannot find forecast initialization time")

        # Convert step (timedelta) to absolute time
        steps = temp[time_dim].values
        absolute_times = [init_time + pd.Timedelta(step) for step in steps]

        # Create new coordinate and swap dimensions to avoid conflicts
        temp = temp.assign_coords({"valid_time": (time_dim, absolute_times)})
        temp = temp.swap_dims({time_dim: "valid_time"})
        temp = temp.drop_vars(time_dim)  # drop old step coord
        if "time" in temp.coords and "time" not in temp.dims:
            temp = temp.drop_vars("time")  # drop scalar init time
        temp = temp.rename({"valid_time": "time"})
        time_dim = "time"

    time_vals = temp[time_dim].values

    if len(time_vals) > 1:
        time_delta = pd.Timedelta(time_vals[1] - time_vals[0])
        if time_delta > pd.Timedelta(hours=1):
            print(f"Interpolating from {time_delta} to hourly...")
            # Create hourly time index
            hourly_index = pd.date_range(
                start=time_vals[0],
                end=time_vals[-1],
                freq='h'  # lowercase 'h' for pandas 2.x
            )
            temp = temp.interp({time_dim: hourly_index}, method="linear")
            print(f"Interpolated to {len(hourly_index)} hourly time steps")


    # Compute heating degree days
    heating_demand = xr.apply_ufunc(np.maximum, BASE_TEMP - temp, 0)

    # Load population data
    print(f"Loading population from {args.population}")
    population_density = (
        xr.open_dataarray(args.population)
        .sel(raster=slice(1, 5))
        .assign_coords(pop_year=("raster", GPWV4_YEARS))
        .swap_dims({"raster": "pop_year"})
        .drop_vars("raster")
        .interp_like(heating_demand)  # interpolate onto HDD grid
    )

    # Save weighted and unweighted HDD (same format as ERA5)
    print(f"Saving to {args.outfile}")
    xr.Dataset(
        {
            "pop_density": population_density,
            "heating_demand": heating_demand,
        }
    ).to_netcdf(args.outfile, format="NETCDF4")
    print("Done!")


if __name__ == "__main__":
    main()
