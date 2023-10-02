import cadquery as cq
import geopandas
import pandas as pd
from cadquery import exporters
import json
import matplotlib.pyplot as plt

# exporters.export(result, "./mesh_test.stl")

files = ["base", "groundfloor", "upperfloor", "rooftops"]


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
        extrude_by = building_part_top - building_part_bottom
        
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
    cutout_shape = cq.Workplane("XY").rect(10, 10)

    # Cut the shape into the bottom of the main solid
    solid = solid.cut(cutout_shape.extrude(1))

    return solid


def cut_text_on_front():
    # text = workplane.text("Z", 5, -1.0).translate((45, 0, 200))
    # test = test.faces(">Z").cut(text)
    pass


if __name__ == "__main__":
    gdf = read_geojson_files()
    buildings_ids = list(gdf["building_id"].unique())

    count = 0
    for building_id in buildings_ids:
        if count < 10:
            count += 1
            continue

        building = gdf[gdf["building_id"] == building_id]

        cad_obj = make_cq_workplane_with_building(building.copy())

        import os

        exporters.export(cad_obj, building_id + ".stl")
        print("exported", cad_obj, building_id + ".stl")
        exit()


# grasbrook_gdf = geopandas.read_file("grasbrook.geojson")
# print(type(grasbrook_gdf.iloc[0]))


# grasbrook_gdf["centroid"] = grasbrook_gdf.geometry.centroid
# centroid = grasbrook_gdf.iloc[0]["centroid"]
# grasbrook_gdf = grasbrook_gdf.translate(-centroid.x, -centroid.y)
# minx, miny, maxx, maxy = grasbrook_gdf.total_bounds

# print("total bounds", minx, miny, maxx, maxy)
# grasbrook_gdf.plot()

# gb_json = json.loads(grasbrook_gdf.to_json())


# pol = gb_json["features"][0]["geometry"]["coordinates"]
# pol = pol[0]

# workplane = cq.Workplane("XY")
# polyline = workplane.polyline(pol).close()
# result = polyline.extrude(100)
# test = result.union(workplane.box(100, 100, 100, centered=True).translate((0, 0, 150)))
# text = workplane.text("Z", 5, -1.0).translate((45, 0, 200))

# test = test.faces(">Z").cut(text)
# print("hello")
# display(test)
