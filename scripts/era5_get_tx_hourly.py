"""
Download ERA5 2m temperature data for Texas from Google's ARCO-ERA5.
Much faster than the CDS API - no queue times.
"""

import argparse
import os

import xarray as xr

# Texas bounding box (in -180 to 180 convention)
X0, X1 = (-108, -92)
Y0, Y1 = (25, 38)


def main() -> None:
    """Download ERA5 hourly 2m temperature for Texas (Jan, Feb, Dec of given year)"""

    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("-o", "--outfile", type=str, required=True)
    args = parser.parse_args()

    year = args.year

    # Google ARCO-ERA5 (public, no auth needed)
    # Full hourly data on single levels
    url = "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"

    print(f"Opening ARCO-ERA5 dataset...")
    ds = xr.open_zarr(
        url,
        chunks={"time": 24},
        consolidated=True,
    )

    # Select 2m temperature
    print("Selecting 2m temperature...")
    t2m = ds["2m_temperature"]

    # Check longitude convention
    lon_vals = t2m.longitude.values
    print(f"Longitude range in dataset: {lon_vals.min():.1f} to {lon_vals.max():.1f}")

    # Convert Texas bounds if dataset uses 0-360
    if lon_vals.max() > 180:
        lon0 = X0 + 360  # -108 -> 252
        lon1 = X1 + 360  # -92 -> 268
        print(f"Using 0-360 convention: lon {lon0} to {lon1}")
    else:
        lon0, lon1 = X0, X1

    # Select months FIRST (before spatial subset to avoid loading all data)
    datasets = []

    # January and February of the target year
    for month in [1, 2]:
        print(f"Loading {year}-{month:02d}...")
        # Select time first, then spatial subset
        month_data = t2m.sel(time=f"{year}-{month:02d}")
        month_data = month_data.sel(latitude=slice(Y1, Y0), longitude=slice(lon0, lon1))
        print(f"  Shape: {dict(month_data.sizes)}")
        datasets.append(month_data)

    # December of previous year (for winter season grouping)
    dec_year = year - 1
    if dec_year >= 1940:
        print(f"Loading {dec_year}-12...")
        dec_data = t2m.sel(time=f"{dec_year}-12")
        dec_data = dec_data.sel(latitude=slice(Y1, Y0), longitude=slice(lon0, lon1))
        print(f"  Shape: {dict(dec_data.sizes)}")
        datasets.append(dec_data)

    # Combine
    print("Combining months...")
    combined = xr.concat(datasets, dim="time")
    combined = combined.sortby("time")

    # Rename variable to match expected format (keep latitude/longitude coord names)
    combined = combined.rename("t2m")

    # Convert longitude back to -180 to 180 if needed
    if combined.longitude.values.max() > 180:
        combined = combined.assign_coords(longitude=combined.longitude - 360)

    # Convert to dataset
    result = combined.to_dataset()

    # Load into memory and save
    print("Downloading and saving to netCDF...")
    os.makedirs(os.path.dirname(args.outfile) or ".", exist_ok=True)
    result.to_netcdf(args.outfile)
    print(f"Saved to {args.outfile}")


if __name__ == "__main__":
    main()
