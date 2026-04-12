import numpy as np
import xarray as xr

from geospatial_change_detection import config


def calculate_ndvi(composite: xr.DataArray, verbose: bool = config.VERBOSE) -> xr.DataArray:
    """
    Calculates the NDVI index xarray from a composite based on NIR and Red bands.

    Args:
        composite: An xarray DataArray with 'B08' (NIR) and 'B04' (Red) bands.
        verbose: Verbosity mode.

    Returns:
        An xarray DataArray containing the NDVI values.
    """
    # Selecting the bands needed for computing the NDVI values
    nir = composite.sel(band="B08").astype(np.float32)
    red = composite.sel(band="B04").astype(np.float32)

    # Calculating NDVI with a small epsilon added to the denominator to avoid division by zero
    ndvi = (nir - red) / (nir + red + 1e-8)
    ndvi = ndvi.rename("ndvi")

    print("NDVI calculation complete.")

    return ndvi
