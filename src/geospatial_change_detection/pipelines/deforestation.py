from pathlib import Path
from typing import Union

import xarray as xr
from numpy import ndarray, dtype, float64

from geospatial_change_detection import config
from geospatial_change_detection.core import visualize, vectorize, aoi, fetch, composite, filesystem
from geospatial_change_detection.indices import change
from geospatial_change_detection.reports import summarize
from geospatial_change_detection.indices.ndvi import calculate_ndvi


def _process_period(
        start: str,
        end: str,
        bounds_wgs84: ndarray[tuple[int], dtype[float64]],
        bounds_target_crs: ndarray[tuple[int], dtype[float64]],
        target_crs: int,
        label: str,
        filename: str,
        verbose: bool = config.VERBOSE
) -> xr.DataArray:
    """
        Compute NDVI for a given timeframe.

        Args:
            start: Start date in ISO format.
            end: End date in ISO format.
            bounds_wgs84: Bounding box in EPSG:4326.
            bounds_target_crs: Bounding box in target CRS.
            target_crs: CRS used for raster processing.
            label: Identifier for console print.
            filename: Identifier for output file naming.
            verbose: Verbosity mode.

        Returns:
            xr.DataArray: NDVI raster for the given timeframe.
    """
    print(f"\nProcessing NDVI for {label} [{start}/{end}]")

    # Fetching Sentinel-2 scenes from the API from the desired region within the specified timeframe
    scenes = fetch.search_stac_scenes(bbox=bounds_wgs84.tolist(), datetime=f"{start}/{end}", verbose=verbose)

    # Creating the median composite in the specified AOI
    median_composite = composite.create_median_composite(
        scenes_dict=scenes,
        bbox=bounds_target_crs.tolist(),
        target_crs=target_crs,
        verbose=verbose
    )

    # Computing the NDVI index
    ndvi = calculate_ndvi(composite=median_composite, verbose=verbose)

    # Saving the results
    raster_path = config.RASTERS_DIR / f"{filename}.tif"
    ndvi.rio.to_raster(raster_path)
    visualize.save_raster_plot(
        raster=ndvi,
        filepath=config.FIGURES_DIR / f"{filename}.png",
        title=f"NDVI for Rondônia, Brazil ({start} to {end})",
        cmap=config.NDVI_CMAP,
        verbose=verbose
    )

    return ndvi


def run_deforestation_pipeline(aoi_path: Union[str, Path] = config.DEFAULT_DEFORESTATION_AOI_PATH, verbose: bool = config.VERBOSE):
    """
    Executes the full deforestation pipeline. By default, the analysis is performed on the Rondônia region in Brazil,
    a well-documented deforestation hotspot in the Amazon over recent decades.
    """

    print("Starting deforestation hotspot detection pipeline")

    # Setting up all the output directories
    filesystem.create_output_directories(verbose=verbose)

    # Loading the desired area of interest (by default in this case as mentioned Rondônia, Brazil) in the desired CRS
    # and transforming the total bounds to 4326 CRS for the sake of Planetary Computer compatibility
    # clarification: STAC API bounding box queries typically require coordinates in WGS84 (EPSG:4326) geographic CRS.
    aoi_gdf = aoi.load_aoi(aoi_path=aoi_path, verbose=verbose)
    bounds_wgs84 = aoi_gdf.to_crs("EPSG:4326").total_bounds
    bounds_target_crs, target_crs = aoi.get_aoi_bounds_and_crs(aoi_gdf)

    # Processing NDVI for periods 1 and 2
    p1_ndvi = _process_period(
        start=config.DEFORESTATION_PERIOD_1_START,
        end=config.DEFORESTATION_PERIOD_1_END,
        bounds_wgs84=bounds_wgs84,
        bounds_target_crs=bounds_target_crs,
        target_crs=target_crs,
        label="period 1",
        filename="period1_ndvi",
        verbose=verbose
    )
    p2_ndvi = _process_period(
        start=config.DEFORESTATION_PERIOD_2_START,
        end=config.DEFORESTATION_PERIOD_2_END,
        bounds_wgs84=bounds_wgs84,
        bounds_target_crs=bounds_target_crs,
        target_crs=target_crs,
        label="period 2",
        filename="period2_ndvi",
        verbose=verbose
    )

    print("\nPerforming vegetation loss detection")

    ndvi_diff = change.calculate_ndvi_change(p1_ndvi=p1_ndvi, p2_ndvi=p2_ndvi, verbose=verbose)
    hotspot_mask = change.detect_vegetation_loss(p1_ndvi=p1_ndvi, ndvi_diff=ndvi_diff, verbose=verbose)

    # Saving the analysis results
    change_raster_path = config.RASTERS_DIR / "ndvi_change.tif"
    ndvi_diff.rio.to_raster(change_raster_path)
    mask_raster_path = config.RASTERS_DIR / "hotspot_mask.tif"
    hotspot_mask.rio.to_raster(mask_raster_path, dtype="uint8")

    visualize.save_raster_plot(
        raster=ndvi_diff,
        filepath=config.FIGURES_DIR / "ndvi_change.png",
        title=f"NDVI Change for Rondônia, Brazil (Period 2 - Period 1)",
        cmap=config.NDVI_CHANGE_CMAP
    )

    print("\nVectorizing and cleaning hotspots")

    hotspots_raw = vectorize.vectorize_raster(hotspot_mask)
    hotspots_clean = vectorize.clean_hotspots(hotspots_raw)

    # Saving the hotspots after noise filtering
    hotspots_path = config.VECTORS_DIR / "deforestation_hotspots.geojson"
    hotspots_clean.to_file(hotspots_path, driver="GeoJSON")
    print(f"Saved cleaned hotspots to: {hotspots_path}")

    # Preparing and saving textual reports
    print("\nGenerating summary report")
    summary_df = summarize.summarize_hotspots(hotspots_clean)

    csv_path = config.REPORTS_DIR / "summary_report.csv"
    json_path = config.REPORTS_DIR / "summary_report.json"
    summary_df.to_csv(csv_path, index=False)
    summary_df.to_json(json_path, orient="records", indent=4)

    print(f"Saved summary report to {csv_path} and {json_path}")
    print("\nSummary:")
    print(summary_df.to_string())

    # Visualizing the detected hotspots over the NDVI raster
    visualize.save_hotspot_overlay_plot(
        raster=ndvi_diff,
        hotspots=hotspots_clean,
        filepath=config.FIGURES_DIR / "deforestation_hotspot_overlay.png",
        title="Deforestation Hotspots on NDVI Change",
        label="Hotspots: NDVI decrease below threshold"
    )

    print("\nPipeline execution complete.")
