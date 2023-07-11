import os
import subprocess
from stl import mesh

from stlplace import get_building_height, get_center_bottom_plane

from string import Template



def save_scad_script(filename, center_coords, building_height):

    filepath = buildings_dir + "/" + filename
    
    template = Template(
        """
        module origBuilding() {
            // Center XY
            translate([$ctrx , $ctry, $minz]) {
                import("$filepath");
            }
        }

        difference() {
                origBuilding();

                cube(
                    [20, 20, 1],
                    center=true
                );

                translate([0, 0, $building_height]) {
                    cube(
                    [0.5, 0.5, 1],
                    center=true
                ); 
                }
            }
        """
    )

    scad_text = template.safe_substitute({
        "filepath": filepath,
        "ctrx": center_coords[0],
        "ctry": center_coords[1],
        "minz": -center_coords[2],
        "building_height": building_height
    })


    with open(scad_dir + "/" + filename.replace("stl", "scad")  ,"w") as fp:
        fp.write(scad_text)
        fp.close()




if __name__ == "__main__":

    # walk all files
    buildings_dir = os.getcwd() + "/buildings"
    new_buildings_dir = buildings_dir + "/__retrofit_buildings_with_cutout_calibration_point"
    scad_dir = buildings_dir + "/__retrofit_scad_scripts_calibration_point"

    for dir in [new_buildings_dir, scad_dir]:
        if not os.path.isdir(dir):
            os.mkdir(dir)
    
    for __, __, filenames in os.walk(buildings_dir):
        for filename in filenames:
            if not filename[-3:] == "stl":
                continue

            print(filename)
            main_body = mesh.Mesh.from_file(buildings_dir + "/" + filename)

            center_coords = get_center_bottom_plane(main_body)
            building_height = get_building_height(main_body)

            save_scad_script(filename, center_coords, building_height)

            proc = subprocess.Popen([
                "openscad",
                "-o",
                new_buildings_dir + "/" + filename,
                scad_dir + "/" + filename.replace("stl", "scad")
            ])
            try:
                outs, errs = proc.communicate(timeout=15)
            except:
                print("export failed")
                proc.kill()
                outs, errs = proc.communicate()
            proc.kill()






