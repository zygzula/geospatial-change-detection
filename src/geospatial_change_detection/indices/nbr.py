import numpy as np
import xarray as xr

from geospatial_change_detection import config


def calculate_nbr(composite: xr.DataArray, verbose: bool = config.VERBOSE) -> xr.DataArray:
    """
    Calculates the NBR index xarray from a composite based on NIR and SWIR bands.

    Args:
        composite: An xarray DataArray with 'B08' (NIR) and 'B12' (SWIR) bands.
        verbose: Verbosity mode.

    Returns:
        An xarray DataArray containing the NBR values.
    """
    # Selecting the bands needed for computing the NBR values
    nir = composite.sel(band="B08").astype(np.float32)
    swir = composite.sel(band="B12").astype(np.float32)

    # Calculating NBR with a small epsilon added to the denominator to avoid division by zero
    nbr = (nir - swir) / (nir + swir + 1e-8)
    nbr = nbr.rename("nbr")

    print("NBR calculation complete.")

    return nbr