from pathlib import Path

### project structure
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# input data paths
RAW_INPUT_DATA_DIR = DATA_DIR / "raw"
DEFAULT_AOI_PATH = RAW_INPUT_DATA_DIR / "aoi.geojson"

# output data paths
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
VECTORS_DIR = OUTPUTS_DIR / "vectors"
RASTERS_DIR = OUTPUTS_DIR / "rasters"
FIGURES_DIR = OUTPUTS_DIR / "figures"
REPORTS_DIR = OUTPUTS_DIR / "reports"

### analysis parameters
TARGET_CRS = "EPSG:32721"  # suitable for Rondônia, Brazil
MINIMUM_PRE_VEGETATION_NDVI_THRESHOLD = 0.4
MINIMUM_NDVI_CHANGE_THRESHOLD = -0.25
MIN_HOTSPOT_AREA_SQM = 20000  # 2 hectares

### timeframes
PERIOD_1_START = "2020-07-01"
PERIOD_1_END = "2020-08-31"

PERIOD_2_START = "2023-07-01"
PERIOD_2_END = "2023-08-31"

### satellite data fetching (Planetary Computer)
STAC_API_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
SATELLITE_COLLECTION = "sentinel-2-l2a"
ASSET_KEYS = ["B04", "B03", "B02", "B08", "SCL"] # Red, Green, Blue, Near-Infrared, and Scene Classification Layer
CLOUD_AND_SHADOW_CLASSES = [3, 8, 9, 10] # https://docs.sentinel-hub.com/api/latest/data/sentinel-2-l2a/
MAX_CLOUD_COVER_PERCENT = 20 # in %

### visualisation
FIG_DPI = 300
FIG_SIZE = (10, 10)
FIG_FONT_SIZE = 12
NDVI_CMAP = "RdYlGn"
NDVI_CHANGE_CMAP = "RdBu"

### loging
VERBOSE = True