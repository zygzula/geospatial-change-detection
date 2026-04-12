"""
Script to execute the main analysis pipeline.
"""
import sys
from pathlib import Path

# Add the source directory to the Python path
# This allows us to import the project's modules
project_root = Path(__file__).resolve().parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from geospatial_change_detection.pipelines.deforestation import run_deforestation_pipeline

if __name__ == "__main__":
    run_deforestation_pipeline()
