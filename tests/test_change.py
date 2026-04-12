import numpy as np
import xarray as xr

from geospatial_change_detection.indices.change import calculate_ndvi_change, detect_vegetation_loss

def test_calculate_ndvi_change():
    """Test that NDVI change is correctly calculated."""
    # Create dummy data
    p1 = xr.DataArray(np.array([[0.5, 0.8], [0.2, 0.1]]), dims=("y", "x"))
    p2 = xr.DataArray(np.array([[0.3, 0.8], [0.5, 0.1]]), dims=("y", "x"))
    
    change = calculate_ndvi_change(p1, p2, verbose=False)
    
    # Expected change: p2 - p1
    expected = np.array([[-0.2, 0.0], [0.3, 0.0]])
    np.testing.assert_allclose(change.values, expected, atol=1e-6)

def test_detect_vegetation_loss(monkeypatch):
    """Test that vegetation loss detection correctly applies thresholds."""
    # Mock config thresholds for predictable testing
    import geospatial_change_detection.config as config
    monkeypatch.setattr(config, "MINIMUM_PRE_VEGETATION_NDVI_THRESHOLD", 0.4)
    monkeypatch.setattr(config, "MINIMUM_NDVI_CHANGE_THRESHOLD", -0.2)

    p1 = xr.DataArray(np.array([[0.5, 0.8], [0.2, 0.6]]), dims=("y", "x"))
    # For pixel (0,0): p1=0.5 (>0.4), change=-0.3 (< -0.2) -> HOTSPOT (1)
    # For pixel (0,1): p1=0.8 (>0.4), change=-0.1 (not < -0.2) -> NO (0)
    # For pixel (1,0): p1=0.2 (<0.4), change=-0.5 (loss but low pre-veg) -> NO (0)
    # For pixel (1,1): p1=0.6 (>0.4), change=0.1 (gain) -> NO (0)
    
    diff = xr.DataArray(np.array([[-0.3, -0.1], [-0.5, 0.1]]), dims=("y", "x"))
    
    hotspots = detect_vegetation_loss(p1, diff, verbose=False)
    
    expected = np.array([[1, 0], [0, 0]], dtype=np.uint8)
    np.testing.assert_array_equal(hotspots.values, expected)
