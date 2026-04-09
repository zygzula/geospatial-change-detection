from typing import Dict, Any

import planetary_computer as pc
import pystac_client
from pystac_client.item_search import (
    BBoxLike, DatetimeLike
)

from qgis_python_miniproject import config


def search_stac_scenes(
        bbox: BBoxLike,
        datetime: DatetimeLike,
        max_cloud_percent: float = config.MAX_CLOUD_COVER_PERCENT,
        verbose: bool = config.VERBOSE
) -> Dict[str, Any]:
    """
    Fetching Sentinel-2 scenes from the Planetary Computer STAC API.

    Args:
        bbox: Bounding box [minx, miny, maxx, maxy] in WGS84 (EPSG:4326).
        datetime: Timeframe in 'YYYY-MM-DD/YYYY-MM-DD' format.
        max_cloud_percent: Maximum allowable cloud cover for a scene in percents.
        verbose: Verbosity mode.

    Returns:
        A dictionary of STAC scenes matching the requested criteria.
    """
    # Establishing a connection with Planetary Computer STACK API
    stac_api = pystac_client.Client.open(
        config.STAC_API_URL,
        modifier=pc.sign_inplace
    )
    if verbose:
        print(f"Establishing connection with STAC API: {config.STAC_API_URL}.")

    # Performing a search request for sentinel-2-l2a collection within the desired timeframe and boundary box and
    # with cloud coverage smaller than the defined threshold
    scenes = stac_api.search(
        collections=[config.SATELLITE_COLLECTION],
        bbox=bbox,
        datetime=datetime,
        query={"eo:cloud_cover": {"lt": max_cloud_percent}},
    )
    if verbose:
        print(
            f"Fetching [{config.SATELLITE_COLLECTION}] collection ({datetime}; max_cloud_percent: {max_cloud_percent}; {bbox}).")

    scenes_dict = scenes.item_collection_as_dict()
    print(f"Found {len(scenes_dict['features'])} scenes for the period {datetime}.")

    return scenes_dict
