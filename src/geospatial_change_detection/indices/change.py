import numpy as np
import xarray as xr

from geospatial_change_detection import config


def calculate_ndvi_change(
        p1_ndvi: xr.DataArray,
        p2_ndvi: xr.DataArray,
        verbose: bool = config.VERBOSE
) -> xr.DataArray:
    """
    Calculates the difference in NDVI between two periods.

    Args:
        p1_ndvi: NDVI DataArray for the first period.
        p2_ndvi: NDVI DataArray for the second period.
        verbose: Verbosity mode.

    Returns:
        A DataArray representing the change in NDVI (NDVI2 - NDVI1).
    """
    # Aligning both NDVI DataArrays to ensure that only the parts where both DataArrays have values are processed
    p1_ndvi_aligned, p2_ndvi_aligned = xr.align(p1_ndvi, p2_ndvi, join="inner")

    ndvi_change = p2_ndvi_aligned - p1_ndvi_aligned
    ndvi_change = ndvi_change.rename("ndvi_change")

    print("NDVI change calculation complete.")

    return ndvi_change


def calculate_nbr_change(
        p1_nbr: xr.DataArray,
        p2_nbr: xr.DataArray,
        verbose: bool = config.VERBOSE
) -> xr.DataArray:
    """
    Calculates the difference in NBR between two periods.

    Args:
        p1_nbr: NBR DataArray for the first period.
        p2_nbr: NBR DataArray for the second period.
        verbose: Verbosity mode.

    Returns:
        A DataArray representing the change in NDVI (NDVI2 - NDVI1).
    """
    # Aligning both NDVI DataArrays to ensure that only the parts where both DataArrays have values are processed
    p1_nbr_aligned, p2_nbr_aligned = xr.align(p1_nbr, p2_nbr, join="inner")

    nbr_change = p1_nbr_aligned - p2_nbr_aligned
    nbr_change = nbr_change.rename("nbr_change")

    print("NBR change calculation complete.")

    return nbr_change


def detect_vegetation_loss(
        p1_ndvi: xr.DataArray,
        ndvi_diff: xr.DataArray,
        verbose: bool = config.VERBOSE
) -> xr.DataArray:
    """
    Detects vegetation loss hotspots based on defined thresholds. For the hotspot to be detected in a particular spot:
     - the (p2 - p1) value needs to be bigger than the predefined minimum change threshold
     - the p1 value needs to be bigger than the predefined minimum vegetation threshold

    Args:
        p1_ndvi: NDVI DataArray for the first period.
        ndvi_diff: NDVI DataArray representing the change in NDVI.
        verbose: Verbosity mode.

    Returns:
        A binary DataArray where 1 represents a vegetation loss hotspot and 0 represents no significant loss.
    """
    # Aligning both NDVI DataArrays to ensure that only the parts where both DataArrays have values are processed
    p1_ndvi_aligned, ndvi_diff_aligned = xr.align(p1_ndvi, ndvi_diff, join="inner")

    # Creating the initial vegetation mask to investigate if the initial NDVI was high enough to say that there
    # was some vegetation in a place in the first place. I there was no vegetation initially then we cannot call it
    # a vegetation loss
    is_initial_vegetation_sufficient = p1_ndvi_aligned > config.MINIMUM_PRE_VEGETATION_NDVI_THRESHOLD

    # Creating the significant loss mask to investigate if the NDVI decrease is _smaller_ than the predefined minimum change threshold
    is_loss_significant = ndvi_diff_aligned < config.MINIMUM_NDVI_CHANGE_THRESHOLD

    vegetation_loss_hotspot_mask = (is_initial_vegetation_sufficient & is_loss_significant).astype(np.uint8)
    vegetation_loss_hotspot_mask = vegetation_loss_hotspot_mask.rename("vegetation_loss_hotspot_mask")

    print("Vegetation loss hotspot detection complete.")

    return vegetation_loss_hotspot_mask


def detect_burnt_area(
        p1_nbr: xr.DataArray,
        nbr_diff: xr.DataArray,
        verbose: bool = config.VERBOSE
) -> xr.DataArray:
    """
    Detects vegetation loss hotspots based on defined thresholds. For the hotspot to be detected in a particular spot:
     - the (p2 - p1) value needs to be bigger than the predefined minimum change threshold
     - the p1 value needs to be bigger than the predefined minimum vegetation threshold

    Args:
        p1_nbr: NBR DataArray for the first period.
        nbr_diff: NBR DataArray representing the change in NBR.
        verbose: Verbosity mode.

    Returns:
        A binary DataArray where 1 represents a vegetation loss hotspot and 0 represents no significant loss.
    """
    # Aligning both NBR DataArrays to ensure that only the parts where both DataArrays have values are processed
    p1_nbr_aligned, nbr_diff_aligned = xr.align(p1_nbr, nbr_diff, join="inner")

    # Creating the initial vegetation mask to investigate if the initial NBR was high enough to say that there
    # was some vegetation in a place in the first place. I there was no vegetation initially then we cannot call it
    # a vegetation loss
    is_initial_vegetation_sufficient = p1_nbr_aligned > config.MINIMUM_PRE_VEGETATION_NBR_THRESHOLD

    # Creating the significant burn mask
    is_burn_significant = nbr_diff_aligned > config.MINIMUM_DNBR_THRESHOLD

    burnt_area_hotspot_mask = (is_initial_vegetation_sufficient & is_burn_significant).astype(np.uint8)
    burnt_area_hotspot_mask = burnt_area_hotspot_mask.rename("burnt_area_hotspot_mask")

    print("Burnt area hotspot detection complete.")

    return burnt_area_hotspot_mask