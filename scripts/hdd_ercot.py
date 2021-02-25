"""
Compute HDD over a specific region
"""

import argparse

import geopandas as gp
import numpy as np
import regionmask
import xarray as xr


def main() -> None:
    """Run the analysis"""

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--hdd", type=str)
    parser.add_argument("--boundary", type=str)
    parser.add_argument("-o", "--outfile", type=str)
    args = parser.parse_args()

    # get the HDD data
    hdd = xr.open_dataset(args.hdd).rename({"longitude": "lon", "latitude": "lat"})

    # read the mask
    ercot = gp.read_file(args.boundary)
    mask = regionmask.mask_geopandas(ercot, hdd)

    # mask and clip
    masked = hdd.where(mask == 0, drop=True)

    # create weights
    pop_weights = hdd["pop_density"].fillna(0)
    spatial_weights = np.cos(np.deg2rad(hdd["lat"]))

    # take spatial averages
    hdd_ercot = xr.Dataset(
        {
            "pop_weighted": (
                masked["heating_demand"].weighted(pop_weights).mean(dim=["lon", "lat"])
            ),
            "area_weighted": (
                masked["heating_demand"]
                .weighted(spatial_weights)
                .mean(dim=["lon", "lat"])
            ),
        }
    )

    # save
    hdd_ercot.to_netcdf(args.outfile, format="NETCDF4")


if __name__ == "__main__":
    main()
