# GEOJSON TO STL
use geojson2stl.py to convert geojson to STL. 
It will extrude each feature in your geojson by it's "height" attribute and export it to STL.


# USE FOR DCS-COUP
## Cut ArUco-Markers placeholders into buildings

Provide input geojsons in input_geojson folder. 
Provide a geojson for each building part geometry (base, groundfloor, upperfloor, rooftops)
Geojsons need to have elevation_at_bottom, elevation_at_top and building_height attributes.

The script will:
- create an STL object for each building in your input files by extruding and stacking each of the geometries from basement to rooftops.
- Cut a 2cm*2cm rectangle at the bottom of the building. 
- Add a calibration point in the buildings center on the top face.

!Print buildings upside down then.!


# Installation
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt

### See example:
![image](https://user-images.githubusercontent.com/4631906/197495895-c8534e7d-fb28-462b-ab84-5ca7ec036509.png)


