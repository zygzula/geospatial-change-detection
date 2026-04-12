import geopandas as gpd
import pandas as pd


def summarize_hotspots(hotspot_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Creates a textual summary of the detected pipelines hotspots.

    Args:
        hotspot_gdf: A GeoDataFrame of the final hotspot polygons.

    Returns:
        A pandas DataFrame with summary statistics.
    """
    if hotspot_gdf.empty:
        # Returning an empty DataFrame with expected columns if no hotspots are found
        return pd.DataFrame({
            "total_hotspots": [0],
            "total_area_sqm": [0.0],
            "total_area_ha": [0.0],
            "mean_area_ha": [0.0],
            "median_area_ha": [0.0],
        })

    # Ensuring the area is calculated if not already present
    if "area_sqm" not in hotspot_gdf.columns:
        hotspot_gdf["area_sqm"] = hotspot_gdf.geometry.area

    # Converting area to hectares for more readable reporting
    hotspot_gdf["area_ha"] = hotspot_gdf["area_sqm"] / 10000

    # Calculating summary statistics
    total_hotspots = len(hotspot_gdf)
    total_area_sqm = hotspot_gdf["area_sqm"].sum()
    total_area_ha = hotspot_gdf["area_ha"].sum()
    mean_area_ha = hotspot_gdf["area_ha"].mean()
    median_area_ha = hotspot_gdf["area_ha"].median()

    # Creating the summary DataFrame
    summary_df = pd.DataFrame({
        "total_hotspots": [total_hotspots],
        "total_area_sqm": [total_area_sqm],
        "total_area_ha": [total_area_ha],
        "mean_area_ha": [mean_area_ha],
        "median_area_ha": [median_area_ha],
    })

    print("Summary statistics generated.")

    return summary_df
