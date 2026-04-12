from geospatial_change_detection import config


def create_output_directories(verbose: bool = config.VERBOSE):
    dirs = [
        config.VECTORS_DIR,
        config.RASTERS_DIR,
        config.FIGURES_DIR,
        config.REPORTS_DIR,
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        if verbose:
            print(f"Creating output directory: {d}.")

    if verbose:
        print("Output directories created successfully.")
