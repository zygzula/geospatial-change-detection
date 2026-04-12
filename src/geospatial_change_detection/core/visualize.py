from typing import Literal

import matplotlib
from matplotlib.figure import Figure

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

import xarray as xr
import geopandas as gpd
from pathlib import Path

from geospatial_change_detection import config


def _visualise_the_plot(
        ax: Axes,
        fig: Figure,
        title: str,
        xlabel: str,
        ylabel: str,
        aspect: Literal["auto", "equal"] | float,
        filepath: Path,
        verbose: bool = config.VERBOSE
):
    ax.set_title(title, fontsize=config.FIG_FONT_SIZE)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_aspect(aspect)
    plt.tight_layout()
    fig.savefig(filepath, dpi=config.FIG_DPI)
    plt.close(fig)

    if verbose:
        print(f"Saved plot: {filepath}")


def save_raster_plot(
        raster: xr.DataArray,
        filepath: Path,
        title: str,
        cmap: str,
        vmin: float = -1,
        vmax: float = 1,
        verbose: bool = config.VERBOSE
):
    """
    Saves a plot of a raster DataArray to a file.
    """
    fig, ax = plt.subplots(figsize=config.FIG_SIZE)
    raster.plot(ax=ax, cmap=cmap, vmin=vmin, vmax=vmax, cbar_kwargs={"shrink": 0.8})

    _visualise_the_plot(
        ax=ax,
        fig=fig,
        title=title,
        xlabel="Easting",
        ylabel="Northing",
        aspect="equal",
        filepath=filepath,
        verbose=verbose
    )


def save_hotspot_overlay_plot(
        raster: xr.DataArray,
        hotspots: gpd.GeoDataFrame,
        filepath: Path,
        title: str,
        raster_cmap: str = "gray",
):
    """
    Saves a plot of hotspot polygons overlaid on a raster.
    """
    fig, ax = plt.subplots(figsize=config.FIG_SIZE)

    # Plotting the raster in the background
    raster.plot(ax=ax, cmap=raster_cmap, cbar_kwargs={"shrink": 0.8})

    # Plotting the hotspot polygons over the raster if they exist
    if not hotspots.empty:
        hotspots.plot(ax=ax, facecolor="none", edgecolor="red", linewidth=1.5)

    _visualise_the_plot(
        ax=ax,
        fig=fig,
        title=title,
        xlabel="Easting",
        ylabel="Northing",
        aspect="equal",
        filepath=filepath
    )
