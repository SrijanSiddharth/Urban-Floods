import sys, os
from joblib import Parallel, delayed
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "./Urban-Floods/")))
from src.gee_core import floodRiskAnalysis, floodVulnerabilityAnalysis, floodExposureAnalysis, floodHazardAnalysis
import time
import requests
import ee
ee.Authenticate()
ee.Initialize(project='ee-539srijansiddharth')

cities = ['Bhopal', 'Gwalior', 'Indore', 'Jabalpur', 'Sagar', 'Satna', 'Ujjain']
years = list(range(1981, 2024+1, 1)) # 1981-present
assets_dir = 'projects/ee-539srijansiddharth/assets/Smart-Cities-India'


def download_flood_parameter(city,
                             year,
                             func,
                             asset_path,
                             output_dir,
                             filename,
                             band='main',
                             index=None,
                             max_retries=3,
                             retry_delay=5
                             ):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'{filename}.tif'
    filepath = f'{output_dir}/{output_file}'
    
    roi = ee.FeatureCollection(f'{asset_path.strip("/")}/{city}')
    results = func(roi, year)[band]

    if band == 'others':
        image = results[index]['layer']
    else:
        image = results['layer']

    image = image.unmask(-9999)

    attempt = 0
    while attempt < max_retries:
        try:
            url = image.getDownloadURL({
                'scale': 30,
                'region': roi.geometry(),
                'format': 'GeoTIFF',
                'crs': 'EPSG:4326'
            })

            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True, f"Data downloaded to {filename}"
            else:
                attempt += 1
                time.sleep(retry_delay)
        except Exception as e:
            attempt += 1
            time.sleep(retry_delay)
    
    return False, f"Download failed for {filename} after {max_retries} attempts"



# Download Risk
results = Parallel(n_jobs=-1, backend='threading')(
    delayed(download_flood_parameter)(city,
                                      year,
                                      floodRiskAnalysis,
                                      assets_dir,
                                      output_dir=f'./Urban-Floods/data/gee_exports/{city}/{city}_risk',
                                      filename=f'{city}_risk_{year}')
    for city in cities
    for year in years
)

if all(success for success, _ in results):
    print("Risk: ✅ All downloads completed successfully.")
else:
    print("Failed downloads:")
    for success, message in results:
        if not success:
            print(f"    {message}")



# Download Static Features
layer_names = {
    0: 'ndwi',
    1: 'ndvi',
    2: 'dem',
    3: 'tpi',
    4: 'distance'
}

results = Parallel(n_jobs=-1, backend='threading')(
    delayed(download_flood_parameter)(city,
                                      None,
                                      floodVulnerabilityAnalysis,
                                      assets_dir,
                                      output_dir=f'./Urban-Floods/data/gee_exports/{city}',
                                      filename=f'{city}_{layer_names[i]}',
                                      band='others',
                                      index=i)
    for city in cities
    for i in layer_names
)

if all(success for success, _ in results):
    print("Static features: ✅ All downloads completed successfully.")
else:
    print("Failed downloads:")
    for success, message in results:
        if not success:
            print(f"    {message}")



# Download Population
layer_names = {
    0: 'population'
}

results = Parallel(n_jobs=-1, backend='threading')(
    delayed(download_flood_parameter)(city,
                                      year,
                                      floodExposureAnalysis,
                                      assets_dir,
                                      output_dir=f'./Urban-Floods/data/gee_exports/{city}/{city}_{layer_names[i]}',
                                      filename=f'{city}_{layer_names[i]}_{year}',
                                      band='others',
                                      index=i)
    for city in cities
    for year in range(1980, 2030+1, 5)
    for i in layer_names
)

if all(success for success, _ in results):
    print("Population: ✅ All downloads completed successfully.")
else:
    print("Failed downloads:")
    for success, message in results:
        if not success:
            print(f"    {message}")



# Download Rainfall & Runoff
layer_names = {
    0: 'runoff',
    1: 'rainfall'
}

results = Parallel(n_jobs=-1, backend='threading')(
    delayed(download_flood_parameter)(city,
                                      year,
                                      floodHazardAnalysis,
                                      assets_dir,
                                      output_dir=f'./Urban-Floods/data/gee_exports/{city}/{city}_{layer_names[i]}',
                                      filename=f'{city}_{layer_names[i]}_{year}',
                                      band='others',
                                      index=i)
    for city in cities
    for year in years
    for i in layer_names
)

if all(success for success, _ in results):
    print("Rainfall & Runoff: ✅ All downloads completed successfully.")
else:
    print("Failed downloads:")
    for success, message in results:
        if not success:
            print(f"    {message}")
