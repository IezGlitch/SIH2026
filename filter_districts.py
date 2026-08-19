import geopandas as gpd

gdf = gpd.read_file("gadm41_IND_2.json")

bihar = gdf[gdf["NAME_1"] == "Bihar"]

target_districts = ["Katihar", "Gaya", "Begusarai"]
filtered = bihar[bihar["NAME_2"].isin(target_districts)]

print(filtered[["NAME_1", "NAME_2"]])
print(f"\nFound {len(filtered)} districts (expected 3)")

filtered.to_file("target_districts.geojson", driver="GeoJSON")
print("\nSaved to target_districts.geojson")