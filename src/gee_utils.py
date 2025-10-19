import geopandas as gpd
from shapely.geometry import shape
import ee
ee.Authenticate()
ee.Initialize()

def categoricalScoreAndRescale(img, bins, cap=None, Max=5, Min=1):
    numClasses = len(bins) + 1
    
    score = img.lt(bins[0]).multiply(1)  # first bin class = 1
    
    for i in range(len(bins) - 1):
        lower = bins[i]
        upper = bins[i + 1]
        classValue = i + 2
        score = score.where(img.gte(lower).And(img.lt(upper)), classValue)
    
    score = score.where(img.gte(bins[-1]), numClasses)  # last bin class
    
    # Rescale to [Min, Max]
    scoreRescaled = score \
        .subtract(1) \
        .multiply(Max - Min) \
        .divide(numClasses - 1) \
        .add(Min)
    
    if cap is not None:
        scoreRescaled = scoreRescaled.min(cap)
    
    return scoreRescaled

def computeAreasOverTime(collection, roi, scale=30,
                         values=[1,2,3,4,5],
                         labels=None,
                         time_property='system:time_start'):
    if labels is None:
        labels = ['Very Low', 'Low', 'Moderate', 'High', 'Very High']
    if len(labels) != len(values):
        raise ValueError('labels and values must have same length')

    collection = ee.ImageCollection(collection).sort(time_property)
    
    if collection.size().getInfo() == 0:
        return {'years': [], 'areas': {lab: [] for lab in labels}}

    pixelArea = ee.Image.pixelArea().divide(1e6)  # km²

    def per_image(img):
        cls = img.select([0]).rename('class')
        weighted = pixelArea.addBands(cls)

        groups = weighted.reduceRegion(
            reducer=ee.Reducer.sum().group(groupField=1, groupName='class'),
            geometry=roi,
            scale=scale,
            maxPixels=1e13
        ).get('groups')

        groups = ee.List(ee.Algorithms.If(groups, groups, ee.List([])))

        year = ee.Algorithms.If(
            img.get(time_property),
            ee.Date(img.get(time_property)).get('year'),
            img.get('year')
        )

        return ee.Image(1).set('year', year, 'groups', groups)

    mapped = collection.map(per_image)

    years_info = mapped.aggregate_array('year').getInfo()
    groups_info = mapped.aggregate_array('groups').getInfo()

    years = []
    areas_by_label = {lab: [] for lab in labels}

    for i, groups in enumerate(groups_info):
        years.append(int(years_info[i]) if years_info[i] is not None else None)
        year_dict = {lab: 0.0 for lab in labels}
        if groups:
            for g in groups:
                val = int(g['class'])
                if 1 <= val <= len(labels):
                    year_dict[labels[val - 1]] = float(g['sum'])
        for lab in labels:
            areas_by_label[lab].append(year_dict[lab])

    return {'years': years, 'areas': areas_by_label}

def load_roi(city, asset_dir = "projects/ee-539srijansiddharth/assets/Smart-Cities-India"):
    asset_path = f"{asset_dir}/{city}"
    roi = ee.FeatureCollection(asset_path)

    features = roi.getInfo()['features']
    roi_gdf = gpd.GeoDataFrame(
        [f['properties'] for f in features],
        geometry=[shape(f['geometry']) for f in features],
        crs='EPSG:4326'
    )

    bounds = roi_gdf.geometry.bounds.values[0]
    extent = [bounds[0], bounds[2], bounds[1], bounds[3]]

    return roi_gdf, extent
