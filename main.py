import os
import subprocess
from stl import mesh

from stlplace import get_center_xyz

from string import Template



def save_scad_script(filename, coords):

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

            difference() {
                origBuilding();

                cube([20, 20, 20], center=true);
            }

             
             translate([0,0,10]) {
                scale([1.05, 1.05, 1]) {
                    origBuilding();
                }
            }
        

        }

        
        
        """
    )

    scad_text = template.safe_substitute({
        "filepath": filepath,
        "ctrx": coords[0],
        "ctry": coords[1],
        "minz": coords[2]
    })


    with open(scad_dir + "/" + filename.replace("stl", "scad")  ,"w") as fp:
        fp.write(scad_text)
        fp.close()




if __name__ == "__main__":

    # walk all files
    buildings_dir = os.getcwd() + "/buildings"
    new_buildings_dir = buildings_dir + "/__retrofit_buildings_with_cutout"
    scad_dir = buildings_dir + "/__retrofit_scad_scripts"

    for dir in [new_buildings_dir, scad_dir]:
        if not os.path.isdir(dir):
            os.mkdir(dir)
    
    for __, __, filenames in os.walk(buildings_dir):
        for filename in filenames:
            if not filename[-3:] == "stl":
                continue

            main_body = mesh.Mesh.from_file(buildings_dir + "/" + filename
)

            coords = get_center_xyz(main_body)

            save_scad_script(filename, coords)

            proc = subprocess.Popen([
                "openscad",
                "-o",
                new_buildings_dir + "/" + filename,
                scad_dir + "/" + filename.replace("stl", "scad")
            ])
            try:
                outs, errs = proc.communicate(timeout=15)
            except:
                proc.kill()
                outs, errs = proc.communicate()
            proc.kill()






