"""
Download GPW v4 population density data from NASA SEDAC using earthaccess.
Requires an Earthdata login - will prompt for credentials on first run.
"""

import argparse
import glob
import os
import zipfile

import earthaccess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", type=str, required=True)
    args = parser.parse_args()

    output_dir = os.path.dirname(args.outfile)
    os.makedirs(output_dir, exist_ok=True)

    # Login (will prompt for credentials or use cached)
    earthaccess.login()

    # Search for GPW v4 population density
    results = earthaccess.search_data(
        short_name="CIESIN_SEDAC_GPWv4_POPDENS_R11",
        granule_name="*2pt5_min*nc*"
    )

    print(f"Found {len(results)} results")

    if results:
        # Download to target directory
        files = earthaccess.download(results[0], output_dir)
        print(f"Downloaded: {files}")

        downloaded = str(files[0]) if files else None

        if downloaded and downloaded.endswith('.zip'):
            # Extract the zip file
            print(f"Extracting {downloaded}...")
            with zipfile.ZipFile(downloaded, 'r') as zf:
                zf.extractall(output_dir)

            # Find the extracted .nc file
            nc_files = glob.glob(os.path.join(output_dir, "*.nc"))
            if nc_files:
                extracted_nc = nc_files[0]
                print(f"Found extracted file: {extracted_nc}")

                # Rename to expected output filename
                if extracted_nc != args.outfile:
                    os.rename(extracted_nc, args.outfile)
                    print(f"Renamed to: {args.outfile}")

                # Clean up zip file
                os.remove(downloaded)
                print(f"Removed zip file: {downloaded}")
            else:
                raise RuntimeError(f"No .nc file found after extracting {downloaded}")

        elif downloaded and downloaded.endswith('.nc'):
            # Already a netCDF file, just rename
            if downloaded != args.outfile:
                os.rename(downloaded, args.outfile)
                print(f"Renamed to: {args.outfile}")
        else:
            raise RuntimeError(f"Unexpected file format: {downloaded}")
    else:
        raise RuntimeError(
            "No results found. You may need to download manually from: "
            "https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-density-rev11/data-download"
        )


if __name__ == "__main__":
    main()
