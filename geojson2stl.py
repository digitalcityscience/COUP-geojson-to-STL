import cadquery as cq
import geopandas
from cadquery import exporters
import json
from shapely.affinity import scale


def solid_from_coords(workplane, coords_exterior, cut_outs=None, extrude_by=0):
    # create a cad object from geometry

    result = workplane.polyline(coords_exterior).close()

    for cut_out in cut_outs:
        result = result.polyline(cut_out).close()

    if extrude_by:
        result = result.extrude(extrude_by)

    return result


# extrudes and stacks ["base", "groundfloor", "upperfloor", "rooftops"] geometries
def geojson_feature_2_cad_obj(feat: geopandas.GeoDataFrame()):
    # center geometry in workplanes origin
    feat_centroid = feat.iloc[0].geometry.centroid.centroid
    feat["geometry"] = feat.translate(-feat_centroid.x, -feat_centroid.y)

    workplane = cq.Workplane("XY")

    geojson = json.loads(feat.to_json())
    coords_exterior_ring = geojson["features"][0]["geometry"]["coordinates"][0]
    interior_rings = geojson["features"][0]["geometry"]["coordinates"][1:]

    return solid_from_coords(
        workplane, coords_exterior_ring, interior_rings, extrude_by=feat.iloc[0]["height"]
    )


def scale_geometries(gdf, scale_factor: float) -> geopandas.GeoDataFrame():
    gdf["geometry"] = gdf["geometry"].apply(
        lambda geom: scale(geom, xfact=scale_factor, yfact=scale_factor)
    )
    gdf["height"] = gdf["height"] * scale_factor

    return gdf


if __name__ == "__main__":
    """
    PROVIDE GEOJSON WITH POLYGON OR MULTIPOLYGON FEATURES
    EACH FEATURE NEEDS ATTRIBUTE "HEIGHT" THAT IT WILL BE EXTRUDED BY
    """
    # Scale all geometries by a factor
    scale_factor = 1

    # read file
    input_gdf = geopandas.read_file("./input.geojson")

    # reproject to metric coords (HAMBURG)
    input_gdf = input_gdf.set_crs("EPSG:4326", allow_override=True)
    input_gdf = input_gdf.to_crs("EPSG:25832")
    input_gdf = scale_geometries(input_gdf, scale_factor)

    # explode geojson to avoid multi-polygons
    input_gdf = input_gdf.explode().reset_index(drop=True)

    for index, row in input_gdf.iterrows():
        try:
            feat = input_gdf[input_gdf.index == index]
            cad_obj = geojson_feature_2_cad_obj(feat.copy())
            exporters.export(cad_obj, f"{str(index)}.stl")
        except Exception as e:
            print(f"problems with row {index} {row}")
            print(e)
