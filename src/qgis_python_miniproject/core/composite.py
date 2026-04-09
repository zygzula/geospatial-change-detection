import numpy as np
# noinspection PyUnusedImports
import rioxarray
import stackstac
import xarray as xr

from qgis_python_miniproject import config


def create_median_composite(
        scenes_dict: dict,
        bbox: list,
        target_crs: int,
        verbose: bool = config.VERBOSE
) -> xr.DataArray:
    """
    Creates a cloud-filtered median composite from a set of STAC scenes.

    Args:
        scenes_dict: A dictionary of STAC scenes.
        bbox: The bounding box of the AOI.
        target_crs: The target CRS for the output composite.
        verbose: Verbosity mode.

    Returns:
        An xarray DataArray containing the cloud-filtered median composite.
    """
    # Check if there are any scenes present in the dictionary to process
    if not scenes_dict['features']:
        if verbose:
            print(f"scenes_dict keys: {scenes_dict.keys()}.")

        raise ValueError("Cannot create composite: No STAC scenes provided in the dictionary.")

    # Creating the stack with all the parameters adjusted to the further analysis
    stack = stackstac.stack(
        scenes_dict["features"],
        assets=config.DEFORESTATION_ASSET_KEYS,
        resolution=10,
        bounds=tuple(bbox),
        epsg=target_crs,
        dtype=float,
        fill_value=np.nan,
        rescale=True,
    )

    # Dividing the bands to the SCL band and the rest to facilitate performing cloud mask operations
    scl_band = "SCL"
    analysis_bands = [band for band in config.DEFORESTATION_ASSET_KEYS if band != scl_band]

    # Creating a cloud mask
    cloud_mask = stack.sel(band=scl_band).isin(config.CLOUD_AND_SHADOW_CLASSES)

    # Applying the cloud mask to all the bands except the SCL one
    masked_stack = stack.sel(band=analysis_bands).where(~cloud_mask)

    # Computing the median composite over time on all the bands from all the scenes that were not masked by the cloud mask
    median_composite = masked_stack.median(dim="time", skipna=True)

    # Clipping the composite once again as the masking operations may potentially cause little offsets
    clipped_composite = median_composite.rio.clip_box(*bbox)

    print("Median composite created successfully.")

    return clipped_composite
