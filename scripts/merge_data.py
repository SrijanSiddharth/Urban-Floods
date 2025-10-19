import os
import numpy as np
import xarray as xr
import rioxarray
from joblib import Parallel, delayed
os.chdir('./Urban-Floods/scripts')
os.makedirs('../data/merged_data/', exist_ok=True)

cities = ['Bhopal', 'Gwalior', 'Indore', 'Jabalpur', 'Sagar', 'Satna', 'Ujjain']

def load_temporal_feature(folder, var_name, years, city, nodata_val=-9999):
    arrays = []
    
    for year in years:
        pattern = os.path.join(folder, f"{city}_{var_name}_{year}.tif")
        
        da = rioxarray.open_rasterio(pattern, masked=True).squeeze("band", drop=True)
        da = da.where(da != nodata_val)
        da = da.assign_coords(time=year).expand_dims("time")
        arrays.append(da)
    
    if not arrays:
        raise ValueError(f"No files found for {var_name} in {folder}")
    
    return xr.concat(arrays, dim="time").rename(var_name)

def load_static_feature(path, var_name, nodata_val=-9999):
    da = rioxarray.open_rasterio(path, masked=True).squeeze("band", drop=True)
    da = da.where(da != nodata_val)
    return da.rename(var_name)

def export_data(city):
    # Load Temporal and Static data
    risk = load_temporal_feature(f"../data/gee_exports/{city}/{city}_risk", "risk", range(1981, 2024+1), city)
    rainfall = load_temporal_feature(f"../data/gee_exports/{city}/{city}_rainfall", "rainfall", range(1981, 2024+1), city)
    runoff = load_temporal_feature(f"../data/gee_exports/{city}/{city}_runoff", "runoff", range(1981, 2024+1), city)
    population = load_temporal_feature(f"../data/gee_exports/{city}/{city}_population", "population", range(1980, 2020 + 1, 5), city)

    dem = load_static_feature(f"../data/gee_exports/{city}/{city}_dem.tif", "dem")
    ndvi = load_static_feature(f"../data/gee_exports/{city}/{city}_ndvi.tif", "ndvi")
    ndwi = load_static_feature(f"../data/gee_exports/{city}/{city}_ndwi.tif", "ndwi")
    tpi = load_static_feature(f"../data/gee_exports/{city}/{city}_tpi.tif", "tpi")
    dist_water = load_static_feature(f"../data/gee_exports/{city}/{city}_distance.tif", "distance")

    # Merge dataset
    ds = xr.merge(
        [risk, rainfall, runoff, population, dem, ndvi, ndwi, tpi, dist_water],
        join='outer',
        compat='no_conflicts'
    )
    
    for var in ds.data_vars:
        if ds[var].dtype == 'float64':
            ds[var] = ds[var].astype('float32')

    comp = dict(zlib=True, complevel=4)
    encoding = {var: comp for var in ds.data_vars}

    # Export
    ds.to_netcdf(f'../data/merged_data/{city}_raw.nc4', format='NETCDF4', encoding=encoding)

Parallel(n_jobs=1)(delayed(export_data)(city) for city in cities)
