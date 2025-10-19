import pandas as pd
import os, sys, time
from pathlib import Path

os.chdir("./Urban-Floods/scripts")
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "..")))
from src.gee_core import floodVulnerabilityAnalysis, floodExposureAnalysis, floodHazardAnalysis, floodRiskAnalysis
from src.gee_utils import computeAreasOverTime
import ee

ee.Authenticate()
ee.Initialize(project='ee-539srijansiddharth')

cities = pd.read_csv('../data/city_list.csv')

config = {
    "Risk": {
        "years": list(range(1981, 2024 + 1)),
        "func": floodRiskAnalysis
    },
    "Hazard": {
        "years": list(range(1981, 2024 + 1)),
        "func": floodHazardAnalysis
    },
    "Exposure": {
        "years": list(range(1980, 2024 + 1, 5)),
        "func": floodExposureAnalysis
    },
    "Vulnerability": {
        "years": [2019],
        "func": floodVulnerabilityAnalysis
    }
}

output_file = Path("../outputs/flood_params_areas.xlsx")
existing_data = {}
if output_file.exists():
    existing_data = pd.read_excel(output_file, sheet_name=None, header=[0,1], index_col=0)

for sheet in config.keys():
    years = config[sheet]["years"]
    func = config[sheet]["func"]

    columns = pd.MultiIndex.from_product([
        cities,
        ['Very Low', 'Low', 'Moderate', 'High', 'Very High'],
    ], names=['City', 'Category'])

    if sheet in existing_data:
        results = existing_data[sheet]
    else:
        results = pd.DataFrame(columns=columns, index=years).rename_axis('Year', axis=0)
    
    for i, city in enumerate(cities):
        if city in results.columns.get_level_values(0):
            if not results[city].isna().any().any():
                continue

        if i%6 == 0:
            time.sleep(30) # to avoid exceeding limit
        
        roi = ee.FeatureCollection(f'projects/ee-539srijansiddharth/assets/Smart-Cities-India/{city}')
        
        imgs = []
        for y in years:
            cat = func(roi, y)['cat']['layer'].set(
                'system:time_start', ee.Date.fromYMD(y, 1, 1).millis()
            )
            imgs.append(cat)
        img_col = ee.ImageCollection(imgs)
        
        out = computeAreasOverTime(img_col, roi)
        
        for cat in ['Very Low', 'Low', 'Moderate', 'High', 'Very High']:
            results.loc[years, (city, cat)] = out['areas'][cat]

        print(f"[{sheet}] Processed city: {city} ({i+1}/{len(cities)})")
        with pd.ExcelWriter(output_file, engine='openpyxl', mode='a' if output_file.exists() else 'w', if_sheet_exists='replace') as writer:
            results.to_excel(writer, sheet_name=sheet)
    print(f"[{sheet}] All cities processed ✅\n")
