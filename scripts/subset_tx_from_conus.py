"""
Subset Texas data from CONUS ERA5 files.
This is more efficient than downloading TX separately since we already have CONUS data.
"""

import argparse
import os

import xarray as xr

# Texas bounding box (in -180 to 180 convention)
TX_X0, TX_X1 = (-108, -92)
TX_Y0, TX_Y1 = (25, 38)


def main() -> None:
    """Subset TX region from CONUS ERA5 data"""

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infile", type=str, required=True, help="CONUS netCDF file")
    parser.add_argument("-o", "--outfile", type=str, required=True, help="Output TX netCDF file")
    args = parser.parse_args()

    print(f"Reading CONUS data from {args.infile}...")
    ds = xr.open_dataset(args.infile)

    print(f"Subsetting to Texas region...")
    # Subset to Texas bounding box
    tx_ds = ds.sel(
        latitude=slice(TX_Y1, TX_Y0),
        longitude=slice(TX_X0, TX_X1)
    )

    print(f"  Original shape: {dict(ds.sizes)}")
    print(f"  TX subset shape: {dict(tx_ds.sizes)}")

    # Save to output file
    print(f"Saving to {args.outfile}...")
    os.makedirs(os.path.dirname(args.outfile) or ".", exist_ok=True)
    tx_ds.to_netcdf(args.outfile)
    print("Done!")


if __name__ == "__main__":
    main()
