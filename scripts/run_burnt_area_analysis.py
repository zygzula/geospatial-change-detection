import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from geospatial_change_detection.pipelines.burnt_area import run_burnt_area_pipeline

if __name__ == "__main__":
    run_burnt_area_pipeline()
