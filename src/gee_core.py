import ee
from src.gee_utils import categoricalScoreAndRescale
ee.Authenticate()
ee.Initialize()

def floodHazardAnalysis(roi, year):
    # Import datasets
    soil_texture = ee.Image('OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02')
    modis_landcover = ee.ImageCollection('MODIS/061/MCD12Q1')
    chirps_daily = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
    
    landUseYear = 2013
    
    soil_class = soil_texture.select('b0').clip(roi).rename('soil')
    
    # Converting soil textute into soil group
    # A == 1, B == 2,  C == 3, D == 4
    soil_grp = soil_class.expression(
        "(b('soil') > 10) ? 4" +
        ": (b('soil') > 4) ? 3" +
        ": (b('soil') > 1) ? 2" +
        ": (b('soil') > 0) ? 1" +
        ": 0"
    ).rename('soil')
    
    modis = modis_landcover.filter(ee.Filter.calendarRange(landUseYear, landUseYear, 'year'))
    lulc = modis.select('LC_Type1').first().clip(roi).rename('lulc')
    
    # Combined LULC & Soil in single image
    lulc_soil = lulc.addBands(soil_grp)
    
    # Create CN map using an expression
    CN_whole = lulc_soil.expression(
        "(b('soil') == 1) and(b('lulc')==1) ? 35" +
        ": (b('soil') == 1) and(b('lulc')==2) ? 25" +
        ": (b('soil') == 1) and(b('lulc')==3) ? 45" +
        ": (b('soil') == 1) and(b('lulc')==4) ? 39" +
        ": (b('soil') == 1) and(b('lulc')==5) ? 45" +
        ": (b('soil') == 1) and(b('lulc')==6) ? 49" +
        ": (b('soil') == 1) and(b('lulc')==7) ? 68" +
        ": (b('soil') == 1) and(b('lulc')==8) ? 36" +
        ": (b('soil') == 1) and(b('lulc')==9) ? 45" +
        ": (b('soil') == 1) and(b('lulc')==10) ? 30" +
        ": (b('soil') == 1) and(b('lulc')==11) ? 95" +
        ": (b('soil') == 1) and(b('lulc')==12) ? 67" +
        ": (b('soil') == 1) and(b('lulc')==13) ? 72" +
        ": (b('soil') == 1) and(b('lulc')==14) ? 63" +
        ": (b('soil') == 1) and(b('lulc')==15) ? 100" +
        ": (b('soil') == 1) and(b('lulc')==16) ? 74" +
        ": (b('soil') == 1) and(b('lulc')==17) ? 100" +
        ": (b('soil') == 2) and(b('lulc')==1) ? 50" +
        ": (b('soil') == 2) and(b('lulc')==2) ? 55" +
        ": (b('soil') == 2) and(b('lulc')==3) ? 66" +
        ": (b('soil') == 2) and(b('lulc')==4) ? 61" +
        ": (b('soil') == 2) and(b('lulc')==5) ? 66" +
        ": (b('soil') == 2) and(b('lulc')==6) ? 69" +
        ": (b('soil') == 2) and(b('lulc')==7) ? 79" +
        ": (b('soil') == 2) and(b('lulc')==8) ? 60" +
        ": (b('soil') == 2) and(b('lulc')==9) ? 66" +
        ": (b('soil') == 2) and(b('lulc')==10) ? 58" +
        ": (b('soil') == 2) and(b('lulc')==11) ? 95" +
        ": (b('soil') == 2) and(b('lulc')==12) ? 78" +
        ": (b('soil') == 2) and(b('lulc')==13) ? 82" +
        ": (b('soil') == 2) and(b('lulc')==14) ? 75" +
        ": (b('soil') == 2) and(b('lulc')==15) ? 100" +
        ": (b('soil') == 2) and(b('lulc')==16) ? 84" +
        ": (b('soil') == 2) and(b('lulc')==17) ? 100" +
        ": (b('soil') == 3) and(b('lulc')==1) ? 73" +
        ": (b('soil') == 3) and(b('lulc')==2) ? 70" +
        ": (b('soil') == 3) and(b('lulc')==3) ? 77" +
        ": (b('soil') == 3) and(b('lulc')==4) ? 74" +
        ": (b('soil') == 3) and(b('lulc')==5) ? 77" +
        ": (b('soil') == 3) and(b('lulc')==6) ? 79" +
        ": (b('soil') == 3) and(b('lulc')==7) ? 86" +
        ": (b('soil') == 3) and(b('lulc')==8) ? 73" +
        ": (b('soil') == 3) and(b('lulc')==9) ? 77" +
        ": (b('soil') == 3) and(b('lulc')==10) ? 71" +
        ": (b('soil') == 3) and(b('lulc')==11) ? 95" +
        ": (b('soil') == 3) and(b('lulc')==12) ? 85" +
        ": (b('soil') == 3) and(b('lulc')==13) ? 87" +
        ": (b('soil') == 3) and(b('lulc')==14) ? 83" +
        ": (b('soil') == 3) and(b('lulc')==15) ? 100" +
        ": (b('soil') == 3) and(b('lulc')==16) ? 90" +
        ": (b('soil') == 3) and(b('lulc')==17) ? 100" +
        ": (b('soil') == 4) and(b('lulc')==1) ? 79" +
        ": (b('soil') == 4) and(b('lulc')==2) ? 77" +
        ": (b('soil') == 4) and(b('lulc')==3) ? 83" +
        ": (b('soil') == 4) and(b('lulc')==4) ? 80" +
        ": (b('soil') == 4) and(b('lulc')==5) ? 83" +
        ": (b('soil') == 4) and(b('lulc')==6) ? 89" +
        ": (b('soil') == 4) and(b('lulc')==7) ? 89" +
        ": (b('soil') == 4) and(b('lulc')==8) ? 79" +
        ": (b('soil') == 4) and(b('lulc')==9) ? 83" +
        ": (b('soil') == 4) and(b('lulc')==10) ? 78" +
        ": (b('soil') == 4) and(b('lulc')==11) ? 95" +
        ": (b('soil') == 4) and(b('lulc')==12) ? 89" +
        ": (b('soil') == 4) and(b('lulc')==13) ? 89" +
        ": (b('soil') == 4) and(b('lulc')==14) ? 87" +
        ": (b('soil') == 4) and(b('lulc')==15) ? 100" +
        ": (b('soil') == 4) and(b('lulc')==16) ? 92" +
        ": (b('soil') == 4) and(b('lulc')==17) ? 100" +
        ": (b('soil') == 0) ? 100" +
        ": 0"
    )
    
    CN2 = CN_whole.clip(roi).rename('CN2')
    
    CN1 = CN2.expression(
        'CN2 / (2.281 - (0.0128 * CN2))',{
        'CN2': CN2.select('CN2')
        }).rename('CN1')
    
    CN3 = CN2.expression(
        'CN2 /(0.427+(0.00573*CN2))',{
        'CN2': CN2.select('CN2')
        }).rename('CN3')
    
    S_image1 = CN1.expression(
        '(25400/CN1)-254', {
        'CN1': CN1.select('CN1')
    }).rename('S_value1')
    
    S_image2 = CN2.expression(
        '(25400/CN2)-254', {
        'CN2': CN2.select('CN2')
    }).rename('S_value2')
    
    S_image3 = CN3.expression(
        '(25400/CN3)-254', {
        'CN3': CN3.select('CN3')
    }).rename('S_value3')
    
    rainfall = chirps_daily.filter(ee.Filter.date(f'{year}-01-01', f'{year}-12-31')).map(lambda img: img.clip(roi))
    
    listOfImages = rainfall.toList(rainfall.size())
    
    def calculateRunningSum(img):
        img = ee.Image(img)
        index = listOfImages.indexOf(img)
        
        firstIndex = ee.Algorithms.If(index.lte(3), index, index.subtract(4))
        firstImage = ee.Image(listOfImages.get(firstIndex))
        
        secondIndex = ee.Algorithms.If(index.lte(3), index, index.subtract(3))
        secondImage = ee.Image(listOfImages.get(secondIndex))
        
        thirdIndex = ee.Algorithms.If(index.lte(3), index, index.subtract(2))
        thirdImage = ee.Image(listOfImages.get(thirdIndex))
        
        fourthIndex = ee.Algorithms.If(index.lte(3), index, index.subtract(1))
        fourthImage = ee.Image(listOfImages.get(fourthIndex))
        
        change = firstImage\
                .add(secondImage)\
                .add(thirdImage)\
                .add(fourthImage)\
                .add(img)\
                .copyProperties(img, ['system:time_start'])
        
        return change
    
    calculated_list = listOfImages.map(calculateRunningSum)

    AMCcollection = ee.ImageCollection(calculated_list)

    # Define the join and filter
    Join = ee.Join.inner()
    FilterOnStartTime = ee.Filter.equals(
        leftField='system:time_start',
        rightField='system:time_start'
    )
    
    # Join the two collections, passing entries through the filter
    rain_AMC = Join.apply(rainfall, AMCcollection, FilterOnStartTime)
      
    # A function to merge the bands together after a join
    # The bands are referred to as the 'primary' and 'secondary' properties
    def MergeBands(aRow):
        return ee.Image.cat(aRow.get('primary'), aRow.get('secondary'))
    
    merged = rain_AMC.map(MergeBands)
    MergedRain_AMC = ee.ImageCollection(merged)
    
    zeroImage = ee.Image(0)
    
    # Define function for Runoff
    def runoff_func(image):
        AMC = image.select('precipitation_1')
        ppt = image.select('precipitation')
        
        AMCreplaced = S_image2.where(AMC.lte(13), S_image1)
        AMCreplaced2 = AMCreplaced.where(AMC.gt(28), S_image3)
        s_value = AMCreplaced2.select('S_value2')

        Q2 = image.expression(
            '((ppt - (0.2 * S)) ** 2) / (ppt - (0.2 * S) + S)', {
                'ppt': ppt,
                'S': s_value
            })

        Q3 = Q2.where(ppt.lt(s_value.multiply(0.2)), zeroImage)
        return Q3.clip(roi).rename('runoff').copyProperties(image, ['system:time_start'])
    
    runoff =  MergedRain_AMC.map(runoff_func)
    
    # Join the two collections, passing entries through the filter
    JoinedRR = Join.apply(rainfall, runoff, FilterOnStartTime)
    
    RainfallRunoff1 = JoinedRR.map(MergeBands)
    RainfallRunoff = ee.ImageCollection(RainfallRunoff1)
    
    precipitationSum = RainfallRunoff.select('precipitation').sum() # Summing precipitation for the period
    runoffSum = RainfallRunoff.select('runoff').sum() # Summing runoff for the period
    
    # Categorical scoring
    # Percentile bins based on median of rainfall data of India from 1958-2024
    # Percentiles boundaries: 5%, 10%, 12.5%, 25%, 37.5%, 50%, 62.5%, 75%, 82.5%, 90%, 95%, 100%
    rainfallBins = [98, 248, 353, 550, 753, 903, 1050, 1240, 1433, 1804, 2269, 3491]
    rainfallScore = categoricalScoreAndRescale(precipitationSum, rainfallBins)
    
    # Percentile bins based on median of runoff data of India from 1958-2024
    # Percentiles boundaries: 5%, 10%, 12.5%, 25%, 37.5%, 50%, 62.5%, 75%, 82.5%, 90%, 95%, 100%
    runoffBins = [6, 15, 21, 33, 74, 184, 293, 421, 553, 873, 1294, 2499]
    runoffScore = categoricalScoreAndRescale(runoffSum, runoffBins)
    
    # Flood hazard score
    floodHazardScore = rainfallScore.add(runoffScore).rename('flood_hazard')
    
    # Rescale from [2, 10] to [1, 5]
    floodHazardScore = floodHazardScore.subtract(2).divide((10 - 2) / (5 - 1)).add(1)
    
    # Flood hazard categories
    floodHazardCategories = floodHazardScore.where(floodHazardScore.gt(4.2), 5)\
                                            .where(floodHazardScore.gt(3.4).And(floodHazardScore.lte(4.2)), 4)\
                                            .where(floodHazardScore.gt(2.6).And(floodHazardScore.lte(3.4)), 3)\
                                            .where(floodHazardScore.gt(1.8).And(floodHazardScore.lte(2.6)), 2)\
                                            .where(floodHazardScore.lte(1.8), 1)
    
    return {
        'main': {
            'layer': floodHazardScore,
            'vis': {'min': 1, 'max': 5, 'palette': ['blue', 'cyan', 'green', 'yellow', 'red']},
            'name': f'Flood Hazard Score {year}',
            'dtype': 'cat',
            'labels': None
        },
        'others': [
            # {'layer': lulc_soil, 'vis': {}, 'name': f'Soil & LULC {landUseYear}', 'dtype': 'num'},
            # {'layer': CN2, 'vis': {}, 'name': 'CN2 values', 'dtype': 'num'},
            # {'layer': S_image3, 'vis': {}, 'name': 'S3', 'dtype': 'num'},
            # {'layer': S_image2, 'vis': {}, 'name': 'S2', 'dtype': 'num'},
            # {'layer': S_image1, 'vis': {}, 'name': 'S1', 'dtype': 'num'},
            {'layer': runoffSum, 'vis': {'min': 0, 'max': 2000, 'palette': ['red', 'yellow', 'green']}, 'name': f'Runoff {year}', 'dtype': 'num'},
            {'layer': precipitationSum, 'vis': {'min': 0, 'max': 2000, 'palette': ['red', 'yellow', 'green']}, 'name': f'Rainfall {year}', 'dtype': 'num'}
        ],
        'cat': {'layer': floodHazardCategories}
    }

def floodVulnerabilityAnalysis(roi, year):
    # Import datasets
    gsw = ee.Image('JRC/GSW1_4/GlobalSurfaceWater')
    srtm = ee.Image("USGS/SRTMGL1_003")
    l8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
    
    landsatYear = 2019
    
    # Permanent water
    permanent = gsw.select('occurrence').gt(80).selfMask()
    
    # Distance from permanent water
    pxLen = ee.Image.pixelArea().sqrt(); 
    distance = permanent.fastDistanceTransform(1024).sqrt().multiply(pxLen).clip(roi)
    distance = distance.reproject(crs='EPSG:4326', scale=30)
    distance = distance.updateMask(distance.neq(0).And(srtm.mask())) # masking water bodies
    
    # Elevation
    elevation = srtm.clip(roi)
    
    # Topographic Position Index (TPI)
    tpi = elevation.subtract(
        elevation.focalMean(5).reproject(crs='EPSG:4326', scale=30)
    ).rename('TPI')
    
    def cloudMask(image):
        qa = image.select('QA_PIXEL')
        dilated = 1 << 1
        cirrus = 1 << 2
        cloud = 1 << 3
        shadow = 1 << 4
        mask = (
            qa.bitwiseAnd(dilated).eq(0)
              .And(qa.bitwiseAnd(cirrus).eq(0))
              .And(qa.bitwiseAnd(cloud).eq(0))
              .And(qa.bitwiseAnd(shadow).eq(0))
        )
        return image.select(['SR_B1','SR_B2','SR_B3','SR_B4','SR_B5','SR_B6','SR_B7'])\
                    .multiply(0.0000275)\
                    .add(-0.2)\
                    .updateMask(mask)
    
    landsat8 = l8.filterBounds(roi)\
                 .filterDate(f'{landsatYear}-01-01', f'{landsatYear}-12-31')\
                 .map(cloudMask)\
                 .median()\
                 .clip(roi)

    bandMap = {
        'RED': landsat8.select('SR_B4'),
        'NIR': landsat8.select('SR_B5'),
        'GREEN': landsat8.select('SR_B3')
    }
    
    # NDVI
    ndvi = landsat8.expression(
        '(NIR - RED) / (NIR + RED)',
        bandMap
    ).rename('NDVI')
    
    # NDWI
    ndwi = landsat8.expression(
        '(GREEN - NIR) / (GREEN + NIR)',
        bandMap
    ).rename('NDWI')
    
    # Categorical scoring
    distanceScore = distance.where(distance.gt(4000), 1)\
                            .where(distance.gt(3000).And(distance.lte(4000)), 2)\
                            .where(distance.gt(2000).And(distance.lte(3000)), 3)\
                            .where(distance.gt(1000).And(distance.lte(2000)), 4)\
                            .where(distance.lte(1000), 5)

    elevScore = elevation.updateMask(distance.neq(0))\
                         .where(elevation.gt(20), 1)\
                         .where(elevation.gt(15).And(elevation.lte(20)), 2)\
                         .where(elevation.gt(10).And(elevation.lte(15)), 3)\
                         .where(elevation.gt(5).And(elevation.lte(10)), 4)\
                         .where(elevation.lte(5), 5)
    
    topoScore = tpi.updateMask(distance.neq(0))\
                   .where(tpi.gt(0), 1)\
                   .where(tpi.gt(-2).And(tpi.lte(0)), 2)\
                   .where(tpi.gt(-4).And(tpi.lte(-2)), 3)\
                   .where(tpi.gt(-6).And(tpi.lte(-4)), 4)\
                   .where(tpi.lte(-6), 5)
    
    vegScore = ndvi.updateMask(distance.neq(0))\
                   .where(ndvi.gt(0.8), 1)\
                   .where(ndvi.gt(0.6).And(ndvi.lte(0.8)), 2)\
                   .where(ndvi.gt(0.4).And(ndvi.lte(0.6)), 3)\
                   .where(ndvi.gt(0.2).And(ndvi.lte(0.4)), 4)\
                   .where(ndvi.lte(0.2), 5)
    
    wetScore = ndwi.updateMask(distance.neq(0))\
                   .where(ndwi.gt(0.6), 5)\
                   .where(ndwi.gt(0.2).And(ndwi.lte(0.6)), 4)\
                   .where(ndwi.gt(-0.2).And(ndwi.lte(0.2)), 3)\
                   .where(ndwi.gt(-0.6).And(ndwi.lte(-0.2)), 2)\
                   .where(ndwi.lte(-0.6), 1)
    
    # Flood vulnerability score
    w = 0.85
    floodVulnerabilityScore = (distanceScore.multiply(w)).add(topoScore).add(vegScore).add(wetScore).add(elevScore)\
                                            .rename('flood_vulnerability')
    
    # Scale to [1, 5]
    floodVulnerabilityScore = floodVulnerabilityScore.subtract(w + 4).multiply(1 / (w + 4)).add(1)

    # Flood vulnerability categories
    floodVulnerabilityCategories = floodVulnerabilityScore.where(floodVulnerabilityScore.gt(4.2), 5)\
                                                          .where(floodVulnerabilityScore.gt(3.4).And(floodVulnerabilityScore.lte(4.2)), 4)\
                                                          .where(floodVulnerabilityScore.gt(2.6).And(floodVulnerabilityScore.lte(3.4)), 3)\
                                                          .where(floodVulnerabilityScore.gt(1.8).And(floodVulnerabilityScore.lte(2.6)), 2)\
                                                          .where(floodVulnerabilityScore.lte(1.8), 1)

    return { 
            'main': {
                'layer': floodVulnerabilityScore,
                'vis': {'min': 1, 'max': 5, 'palette': ['blue', 'cyan', 'green', 'yellow', 'red']},
                'name': 'Flood Vulnerability Score',
                'dtype': 'cat',
                'labels': None
                },
            'others': [
                {'layer': ndwi, 'vis': {'min': -1, 'max': 1, 'palette': ['red', 'white', 'blue']}, 'name': 'NDWI', 'dtype': 'num'},
                {'layer': ndvi, 'vis': {'min': -1, 'max': 1, 'palette': ['blue', 'white', 'green']}, 'name': 'NDVI', 'dtype': 'num'},
                {'layer': elevation, 'vis': {'min': 0, 'max': 100, 'palette': ['green', 'yellow', 'red', 'white']}, 'name': 'DEM', 'dtype': 'num'},
                {'layer': tpi, 'vis': {'min': -5, 'max': 5, 'palette': ['blue', 'yellow', 'red']}, 'name': 'TPI', 'dtype': 'num'},
                {'layer': distance, 'vis': {'min': 0, 'max': 5000, 'palette': ['blue', 'cyan', 'green', 'yellow', 'red']}, 'name': 'Distance from Water', 'dtype': 'num'},
                {'layer': permanent.clip(roi), 'vis': {'palette': ['blue']}, 'name': 'Permanent Water', 'dtype': 'cat', 'labels': ['Water']}
                ],
            'cat': {'layer': floodVulnerabilityCategories}
            }

def floodExposureAnalysis(roi, year):
    # Import datasets
    pop = ee.ImageCollection('JRC/GHSL/P2023A/GHS_POP')
    
    popYear = max(1975, year - (year % 5)) # Only available at an interval of 5 years from 1975
    
    # Prepare population image
    pop_img = pop.filterDate(f'{popYear}-01-01', f'{popYear}-12-31').first()
    pop_img = pop_img.clip(roi).reproject(crs='EPSG:4326', scale=30)
    
    # Categorical scoring
    # Percentile bins based on median of population data of some most densely populated Indian cities from 1975-2020
    # Percentile bin boundaries: 55%, 65%, 75%, 85%, 95%, 97.5%, 99%, 99.5%, 99.75%, 99.9%, 100%
    bins = [57, 117, 183, 241, 408, 492, 607, 697, 793, 956, 1527]
    popScore = categoricalScoreAndRescale(pop_img, bins, 4.25)
    
    # Flood exposure score
    floodExposureScore = popScore.rename('flood_exposure')
    
    # Flood exposure categories
    floodExposureCategories = floodExposureScore.where(floodExposureScore.gt(4.2), 5)\
                                                .where(floodExposureScore.gt(3.4).And(floodExposureScore.lte(4.2)), 4)\
                                                .where(floodExposureScore.gt(2.6).And(floodExposureScore.lte(3.4)), 3)\
                                                .where(floodExposureScore.gt(1.8).And(floodExposureScore.lte(2.6)), 2)\
                                                .where(floodExposureScore.lte(1.8), 1)
    
    return {
        'main': {
            'layer': floodExposureScore,
            'vis': {'min': 1, 'max': 5, 'palette': ['violet', 'blue', 'green', 'gold', 'red']},
            'name': f'Flood Exposure Score {popYear}',
            'dtype': 'cat',
            'labels': None
            },
        'others': [
            {'layer': pop_img, 'vis': {'min': 0, 'max': 1000, 'palette': ['green', 'yellow', 'red']}, 'name': f'Population {popYear}', 'dtype': 'num'}
            ],
        'cat': {'layer': floodExposureCategories}
    }

def floodRiskAnalysis(roi, year):
    params = dict(roi=roi, year=year)
    
    vulnerability = floodVulnerabilityAnalysis(**params)
    exposure = floodExposureAnalysis(**params)
    hazard = floodHazardAnalysis(**params)
    
    floodVulnerabilityScore = vulnerability['main']['layer']
    floodExposureScore = exposure['main']['layer']
    floodHazardScore = hazard['main']['layer']
    
    # Flood risk
    floodRiskScore = floodVulnerabilityScore.multiply(floodExposureScore).multiply(floodHazardScore).rename('risk')
    
    # Flood risk categories
    riskMax = 50
    tol = 2.5 # tolerance
    floodRiskCategories = floodRiskScore.where(floodRiskScore.gt(riskMax - tol), 5)\
                                        .where(floodRiskScore.gt(3 * riskMax / 4 - tol).And(floodRiskScore.lte(riskMax - tol)), 4)\
                                        .where(floodRiskScore.gt(2 * riskMax / 4 - tol).And(floodRiskScore.lte(3 * riskMax / 4 - tol)), 3)\
                                        .where(floodRiskScore.gt(riskMax / 4 - tol).And(floodRiskScore.lte(2 * riskMax / 4 - tol)), 2)\
                                        .where(floodRiskScore.lte(riskMax / 4 - tol), 1)
    
    return {
        'main': {
            'layer': floodRiskScore,
            'vis': {'min': 1, 'max': riskMax, 'palette': ['blue', 'cyan', 'green', 'yellow', 'red']},
            'name': f'Flood Risk Score {year}',
            'dtype': 'cat',
            'labels': None
        },
        'others': [
            {'layer': floodVulnerabilityScore, 'vis': vulnerability['main']['vis'], 'name': vulnerability['main']['name'], 'dtype': 'cat', 'labels': None},
            {'layer': floodExposureScore, 'vis': exposure['main']['vis'], 'name': exposure['main']['name'], 'dtype': 'cat', 'labels': None},
            {'layer': floodHazardScore, 'vis': hazard['main']['vis'], 'name': hazard['main']['name'], 'dtype': 'cat', 'labels': None}
        ],
        'cat': {'layer': floodRiskCategories}
    }
