import geopandas as gpd
import xarray as xr
from rasterio import features
from shapely.geometry import shape

from qgis_python_miniproject import config


def vectorize_raster(
        raster: xr.DataArray,
        label: str = "hotspot",
) -> gpd.GeoDataFrame:
    """
    Vectorizes a binary raster into polygons.

    Args:
        raster: A binary xarray DataArray (0 and 1).
        label: A label for the column containing the vectorized values.

    Returns:
        A GeoDataFrame with polygons for the hotspot (non-zero) areas of the raster.
    """
    crs = raster.rio.crs

    # Extracting the shapes from the raster
    shapes = features.shapes(
        source=raster.values.astype("uint8"),
        mask=raster.notnull().values,
        transform=raster.rio.transform(),
    )

    # Filtering for shapes where the value is 1 (the shapes representing the hotspots)
    hotspot_polygons = [
        shape(geom) for geom, value in shapes if value == 1
    ]

    # Creating a GeoDataFrame object from the hotspot polygons
    gdf = gpd.GeoDataFrame(
        data={label: [1] * len(hotspot_polygons)},
        geometry=hotspot_polygons,
        crs=crs,
    )

    print(f"Vectorized {len(gdf)} polygons.")

    return gdf


def clean_hotspots(hotspot_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Cleans the hotspot polygons from small polygons as there is every likelihood that they are just noise.

    Args:
        hotspot_gdf: GeoDataFrame of hotspot polygons.

    Returns:
        A cleaned GeoDataFrame with small polygons removed.
    """
    # Calculating area of every polygon to enable filtering
    hotspot_gdf["area_sqm"] = hotspot_gdf.geometry.area

    # Filtering the polygons by sufficient area
    cleaned_gdf = hotspot_gdf[hotspot_gdf["area_sqm"] >= config.MIN_HOTSPOT_AREA_SQM].copy()

    num_removed = len(hotspot_gdf) - len(cleaned_gdf)
    print(f"Removed {num_removed} small polygons (area < {config.MIN_HOTSPOT_AREA_SQM} sqm).")

    return cleaned_gdf
