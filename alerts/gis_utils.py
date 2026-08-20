import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
import geopandas as gpd


def raster_to_alert_geometry(raster_path, threshold=100, simplify_tolerance=0.01, min_points=20):
    """
    min_area: minimum polygon area (in square degrees, since we're in EPSG:4326)
              to keep — filters out small noise fragments before dissolving.
    """
    with rasterio.open(raster_path) as src:
        if src.crs.to_string() != 'EPSG:4326':
            raise ValueError(
                f"Raster CRS is {src.crs}, expected EPSG:4326. "
                f"Reproject with `rio warp` before calling this function."
            )

        band1 = src.read(1)
        transform = src.transform
        mask = band1 > threshold

        results = (
            {'properties': {'value': v}, 'geometry': shape(s)}
            for s, v in shapes(band1, mask=mask, transform=transform)
        )
        geoms = list(results)

    if not geoms:
        return None, 0.0

    gdf = gpd.GeoDataFrame(geoms, crs="EPSG:4326")

    # Filter out tiny noise fragments before dissolving
    gdf['point_count'] = gdf.geometry.apply(lambda g: len(g.exterior.coords) if g.geom_type == 'Polygon' else 0)
    gdf = gdf[gdf['point_count'] >= min_points]
    if len(gdf) == 0:
        return None, 0.0

    dissolved = gdf.dissolve()
    dissolved['geometry'] = dissolved['geometry'].simplify(simplify_tolerance)

    final_geom = dissolved.geometry.iloc[0]
    placeholder_confidence = round(float(mask.sum()) / mask.size, 2)

    return final_geom, placeholder_confidence