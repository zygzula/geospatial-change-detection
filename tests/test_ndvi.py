import numpy as np
import xarray as xr

from geospatial_change_detection.indices.ndvi import calculate_ndvi

def test_calculate_ndvi():
    """Test standard NDVI calculation with small epsilon to prevent div by 0."""
    # Create dummy composite with B04 and B08
    # B04 = Red, B08 = NIR
    data = np.array([
        [[0.1, 0.2], [0.0, 0.5]], # B04
        [[0.4, 0.2], [0.0, 0.1]]  # B08
    ])
    
    # coords
    bands = ["B04", "B08"]
    composite = xr.DataArray(data, coords={"band": bands}, dims=("band", "y", "x"))
    
    ndvi = calculate_ndvi(composite, verbose=False)
    
    # Pixel (0,0): (0.4 - 0.1) / (0.4 + 0.1) = 0.3 / 0.5 = 0.6
    # Pixel (0,1): (0.2 - 0.2) / (0.2 + 0.2) = 0.0
    # Pixel (1,0): (0.0 - 0.0) / (0.0 + 0.0 + 1e-8) ≈ 0.0
    # Pixel (1,1): (0.1 - 0.5) / (0.1 + 0.5) = -0.4 / 0.6 = -0.6666...
    
    expected = np.array([
        [0.6, 0.0],
        [0.0, -0.66666667]
    ])
    
    np.testing.assert_allclose(ndvi.values, expected, atol=1e-5)
