import cadquery as cq
import geopandas
import pandas as pd
from cadquery import exporters
import json
import matplotlib.pyplot as plt
from shapely.affinity import scale


# exporters.export(result, "./mesh_test.stl")

files = ["base", "groundfloor", "upperfloor", "rooftops"]


# returns all geojson files projected to metric coords in 1 gdf
def read_geojson_files() -> geopandas.GeoDataFrame():
    gdfs = []
    for filename in files:
        # set building part
        gdf = geopandas.read_file("./input_geojsons/" + filename + ".json")
        gdf["building_part"] = filename

        # reproject to metric coords
        gdf = gdf.set_crs("EPSG:4326", allow_override=True)
        gdf = gdf.to_crs("EPSG:25832")

        # put base geometries to Z=0
        if filename == "base":
            gdf["elevation_at_bottom"] = 0

        gdfs.append(gdf)

    return pd.concat(gdfs)


def solid_from_coords(workplane, coords_exterior, cut_outs=None, extrude_by=0):
    # create a cad object from geometry

    print(coords_exterior)
    # exit()
    result = workplane.polyline(coords_exterior).close()

    for cut_out in cut_outs:
        result = result.polyline(cut_out).close()

    if extrude_by:
        result = result.extrude(extrude_by)

    return result


# extrudes and stacks ["base", "groundfloor", "upperfloor", "rooftops"] geometries
def make_cq_workplane_with_building(building: geopandas.GeoDataFrame()):
    building_centroid = (
        building[building["building_part"] == "base"].iloc[0].geometry.centroid
    )
    building["geometry"] = building.translate(
        -building_centroid.x, -building_centroid.y
    )

    workplane = cq.Workplane("XY")

    for building_part in files:
        print(building_part)
        # read geometry from geojson
        gdf = building[building["building_part"] == building_part]

        if len(gdf.index) == 0:
            continue

        geojson = json.loads(gdf.to_json())
        coords_exterior_ring = geojson["features"][0]["geometry"]["coordinates"][0]
        interior_rings = geojson["features"][0]["geometry"]["coordinates"][1:]

        building_part_bottom = gdf.iloc[0]["elevation_at_bottom"]
        building_part_top = gdf.iloc[0]["elevation_at_top"]
        extrude_by = (building_part_top - building_part_bottom)

        cad_obj = solid_from_coords(
            workplane, coords_exterior_ring, interior_rings, extrude_by=extrude_by
        )

        if building_part == "base":
            # create the cutout for the aruco marker
            cad_obj = cut_marker_placeholder(cad_obj)
        else:
            # translate up on Z axis to level with building part underneath
            cad_obj = cad_obj.translate(
                (0, 0, building_part_bottom)  # + (building_part_height / 2))
            )

        exporters.export(cad_obj, building_part + ".stl")

        workplane = workplane.union(cad_obj)
    
    return workplane


def cut_marker_placeholder(solid):
    # Create the rectangular cutout shape
    cutout_shape = cq.Workplane("XY").rect(20, 20)

    # Cut the shape into the bottom of the main solid
    solid = solid.cut(cutout_shape.extrude(1))

    return solid


def scale_geometries(gdf, scale_factor: float) -> geopandas.GeoDataFrame():
    gdf["geometry"] = gdf["geometry"].apply(
        lambda geom: scale(geom, xfact=scale_factor, yfact=scale_factor)
    )
    gdf["building_height"] = gdf["building_height"] * scale_factor
    gdf["elevation_at_bottom"] = gdf["elevation_at_bottom"] * scale_factor
    gdf["elevation_at_top"] = gdf["elevation_at_top"] * scale_factor

    return gdf


if __name__ == "__main__":
    gdf = read_geojson_files()

    # Scale all geometries by a factor of
    # 2 (scale of 1/500) *1000, as cadquery works in mm not m)
    scale_factor = 2
    gdf = scale_geometries(gdf, scale_factor)
   
    buildings_ids = list(gdf["building_id"].unique())

    for building_id in buildings_ids:
        try:
            building = gdf[gdf["building_id"] == building_id]

            cad_obj = make_cq_workplane_with_building(building.copy())

            exporters.export(cad_obj, building_id + ".stl")
            print("exported", cad_obj, building_id + ".stl")
        except Exception as e:
            print(f"problems with building {building_id}")
            print(e)
            building.to_file("./problems/" + building_id + ".geojson", driver="GeoJSON")