"""
Download ECMWF forecast data (IFS ensemble or AIFS) for Texas.

Uses ECMWF Open Data - free, no authentication required.
https://www.ecmwf.int/en/forecasts/datasets/open-data

Usage:
    python scripts/download_ecmwf_forecast.py --model ens --init 2026012100 --end 2026012823 -o data/raw/ecmwf/forecast_ens.nc
"""

import argparse
import os
from datetime import datetime

import numpy as np
import xarray as xr
from ecmwf.opendata import Client

# Texas bounding box (matching ERA5 script)
X0, X1 = (-108, -92)
Y0, Y1 = (25, 38)


def download_forecast(model: str, init_time: datetime, end_time: datetime, outfile: str,
                     ensemble_member: int = None) -> None:
    """
    Download ECMWF forecast 2m temperature for Texas.

    Parameters
    ----------
    model : str
        Forecast model: 'ens' for IFS ensemble (51 members),
        'hres' for IFS HRES, or 'aifs' for AIFS
    init_time : datetime
        Forecast initialization time
    end_time : datetime
        End of forecast period to download
    outfile : str
        Output netCDF file path
    ensemble_member : int, optional
        For 'ens' model: specific member to download (0-50), or None for all members.
        Use 0 for control forecast.
    """
    # Use AWS as source (generally faster)
    client = Client(source="aws")

    # Lead times needed (hours from init)
    # Start from step 0 (or first available) to end_time
    end_step = int((end_time - init_time).total_seconds() / 3600)

    print(f"Model: {model}")
    print(f"Init time: {init_time}")
    print(f"End time: {end_time}")
    print(f"Max lead time: {end_step}h")

    # Build step list based on model
    # ENS: 3-hourly to 144h, then 6-hourly to 360h
    # HRES/AIFS: 3-hourly to 144h, then 6-hourly to 240h
    steps = []
    for s in range(0, min(end_step + 6, 361)):
        if s <= 144 and s % 3 == 0:
            steps.append(s)
        elif s > 144 and s % 6 == 0:
            steps.append(s)

    print(f"Requesting {len(steps)} steps: {steps[:5]}...{steps[-5:] if len(steps) > 10 else ''}")

    # Download to temporary grib file
    tmp_grib = outfile.replace('.nc', '.grib2')
    os.makedirs(os.path.dirname(outfile) or ".", exist_ok=True)

    # Build request based on model type
    request = {
        "date": init_time.strftime("%Y%m%d"),
        "time": init_time.hour,
        "step": steps,
        "param": "2t",  # 2m temperature
        "target": tmp_grib,
    }

    if model == "ens":
        # IFS Ensemble - perturbed forecasts (50 members) + control
        if ensemble_member is not None:
            if ensemble_member == 0:
                # Control forecast
                request["type"] = "cf"
                request["stream"] = "enfo"
            else:
                # Specific perturbed member
                request["type"] = "pf"
                request["stream"] = "enfo"
                request["number"] = ensemble_member
        else:
            # All members
            request["type"] = "pf"
            request["stream"] = "enfo"
    elif model == "aifs":
        # AIFS model
        request["model"] = "aifs"
        request["type"] = "fc"
        request["stream"] = "oper"
    else:
        # IFS HRES
        request["type"] = "fc"
        request["stream"] = "oper"

    try:
        print(f"Downloading from ECMWF Open Data...")
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                client.retrieve(**request)
                print(f"Downloaded to {tmp_grib}")
                break
            except Exception as e:
                if "SlowDown" in str(e) or "503" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 30  # 30, 60, 90 seconds
                        print(f"Rate limited. Waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                        time.sleep(wait_time)
                    else:
                        raise
                else:
                    raise

        # Open with xarray and subset to Texas
        print("Processing GRIB file...")

        # For ensemble data, we may have multiple datasets
        try:
            ds = xr.open_dataset(tmp_grib, engine="cfgrib")
        except Exception:
            # Try with different filter keys for ensemble
            ds = xr.open_dataset(
                tmp_grib,
                engine="cfgrib",
                backend_kwargs={"filter_by_keys": {"typeOfLevel": "heightAboveGround"}}
            )

        print(f"Dataset variables: {list(ds.data_vars)}")
        print(f"Dataset dims: {dict(ds.sizes)}")

        # Subset to Texas region
        # Handle longitude convention (ECMWF uses 0-360)
        if "longitude" in ds.coords:
            lon_coord = "longitude"
            lat_coord = "latitude"
        else:
            lon_coord = "lon"
            lat_coord = "lat"

        lon_vals = ds[lon_coord].values
        if lon_vals.max() > 180:
            lon0 = X0 + 360 if X0 < 0 else X0
            lon1 = X1 + 360 if X1 < 0 else X1
        else:
            lon0, lon1 = X0, X1

        ds_tx = ds.sel(
            **{
                lat_coord: slice(Y1, Y0),
                lon_coord: slice(lon0, lon1)
            }
        )

        # Convert longitude back to -180 to 180
        if ds_tx[lon_coord].values.max() > 180:
            ds_tx = ds_tx.assign_coords(
                **{lon_coord: ds_tx[lon_coord] - 360}
            )

        # Find temperature variable and convert K to F
        temp_var = None
        for v in ["t2m", "2t", "t"]:
            if v in ds_tx:
                temp_var = v
                break

        if temp_var:
            ds_tx["t2m_f"] = (ds_tx[temp_var] - 273.15) * 9/5 + 32
            ds_tx["t2m_f"].attrs["units"] = "degF"
            ds_tx["t2m_f"].attrs["long_name"] = "2m temperature"

        # Save to netCDF
        ds_tx.to_netcdf(outfile)
        print(f"Saved to {outfile}")

        # Summary stats
        if "number" in ds_tx.dims:
            print(f"Ensemble members: {ds_tx.sizes['number']}")
        print(f"Time steps: {ds_tx.sizes.get('step', ds_tx.sizes.get('time', 'N/A'))}")
        print(f"Spatial shape: {lat_coord}={ds_tx.sizes[lat_coord]}, {lon_coord}={ds_tx.sizes[lon_coord]}")

    finally:
        # Clean up temp file
        if os.path.exists(tmp_grib):
            os.remove(tmp_grib)
            print(f"Cleaned up {tmp_grib}")


def main():
    parser = argparse.ArgumentParser(
        description="Download ECMWF forecast data for Texas"
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=["hres", "ens", "aifs"],
        default="ens",
        help="Forecast model: hres (IFS HRES), ens (IFS ensemble), or aifs"
    )
    parser.add_argument(
        "--init",
        type=str,
        required=True,
        help="Forecast init time as YYYYMMDDHH (e.g., 2026012100 for Jan 21, 2026 00Z)"
    )
    parser.add_argument(
        "--end",
        type=str,
        required=True,
        help="End time as YYYYMMDDHH (e.g., 2026012823 for Jan 28, 2026 23Z)"
    )
    parser.add_argument(
        "-o", "--outfile",
        type=str,
        required=True,
        help="Output netCDF file path"
    )
    parser.add_argument(
        "--member",
        type=int,
        default=None,
        help="For ensemble: specific member to download (0=control, 1-50=perturbed). Default: all members"
    )
    args = parser.parse_args()

    init_time = datetime.strptime(args.init, "%Y%m%d%H")
    end_time = datetime.strptime(args.end, "%Y%m%d%H")

    download_forecast(args.model, init_time, end_time, args.outfile,
                     ensemble_member=args.member)


if __name__ == "__main__":
    main()
