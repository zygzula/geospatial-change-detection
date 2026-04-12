"""
Functions for loading and validating the Area of Interest (AOI).
"""
from pathlib import Path
from typing import Union

import geopandas as gpd

from geospatial_change_detection import config


def load_aoi(aoi_path: Union[str, Path], verbose: bool = config.VERBOSE) -> gpd.GeoDataFrame:
    """
    Loads an Area of Interest (AOI) from a vector file.

    The function ensures that the file exists, can be read by GeoPandas,
    and is projected to the target CRS defined in the project configuration.

    Args:
        aoi_path: Path to the vector file (e.g., GeoJSON, Shapefile).
                  Defaults to the path specified in the config module.

    Returns:
        A GeoDataFrame containing the AOI geometry, in the target CRS.

    Raises:
        FileNotFoundError: If the AOI file does not exist.
        Exception: If the file cannot be read by GeoPandas or is empty.
    """
    aoi_filepath = Path(aoi_path)
    if not aoi_filepath.exists():
        raise FileNotFoundError(f"AOI file not found at: {aoi_filepath}")

    try:
        gdf = gpd.read_file(aoi_filepath)
        if gdf.empty:
            raise ValueError("AOI file is empty.")
    except Exception as e:
        raise Exception(f"Failed to read AOI file: {aoi_filepath}. Error: {e}")

    # Project to the target CRS
    gdf_proj = gdf.to_crs(config.TARGET_CRS)
    if verbose:
        print(f"Projecting GeoDataFrame to CRS: {config.TARGET_CRS}.")

    print(f"Successfully loaded and projected AOI from: {aoi_filepath}")
    return gdf_proj


def get_aoi_bounds_and_crs(aoi_gdf: gpd.GeoDataFrame):
    """
    Extracts the bounding box and CRS from an AOI GeoDataFrame.

    Args:
        aoi_gdf: A GeoDataFrame representing the AOI.

    Returns:
        A tuple containing the bounding box (minx, miny, maxx, maxy)
        and the CRS of the GeoDataFrame.
    """
    bounds = aoi_gdf.total_bounds
    crs = aoi_gdf.crs.to_epsg()

    return bounds, crs
