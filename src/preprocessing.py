import numpy as np
import xarray as xr
from rasterio.enums import Resampling

def mask_water_bodies(ds):
    # Keep valid pixels only across all features and time steps
    mask = np.ones((ds.sizes['y'], ds.sizes['x']), dtype=bool)

    for var in ds.data_vars:
        data = ds[var].values
        
        if 'time' in ds[var].dims:
            data = data[np.any(~np.isnan(data), axis=(1, 2))]
            mask &= np.all(~np.isnan(data), axis=0)
        else:
            mask &= ~np.isnan(data)
    
    ds = ds.where(xr.DataArray(mask, dims=('y', 'x')))
    return ds

def downsample_xarray(ds, target_pixels=200):
    def compute_downsample_factor(ds, target_pixels):
        width = ds.sizes['x']
        height = ds.sizes['y']
        factor_x = width / target_pixels
        factor_y = height / target_pixels
        factor = max(factor_x, factor_y)
        return 1 if factor < 1 else 1 / factor

    downsample_factor = compute_downsample_factor(ds, target_pixels)

    ds = ds.rio.reproject(
        ds.rio.crs,
        shape=(int(ds.sizes['y'] * downsample_factor), int(ds.sizes['x'] * downsample_factor)),
        resampling=Resampling.average
    )
    return ds