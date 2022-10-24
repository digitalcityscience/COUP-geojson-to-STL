import stl
import numpy


"""
THIS LOGIC IS TAKEN FROM 
https://github.com/lar3ry/OpenSCAD---Move-STL-to-origin
"""


# this stolen from numpy-stl documentation
# https://pypi.python.org/pypi/numpy-stl

# find the max dimensions, so we can know the bounding box, getting the height,
# width, length (because these are the step size)...
def find_mins_maxs(obj):
    minx = maxx = miny = maxy = minz = maxz = None
    for p in obj.points:
        # p contains (x, y, z)
        if minx is None:
            minx = p[stl.Dimension.X]
            maxx = p[stl.Dimension.X]
            miny = p[stl.Dimension.Y]
            maxy = p[stl.Dimension.Y]
            minz = p[stl.Dimension.Z]
            maxz = p[stl.Dimension.Z]
        else:
            maxx = max(p[stl.Dimension.X], maxx)
            minx = min(p[stl.Dimension.X], minx)
            maxy = max(p[stl.Dimension.Y], maxy)
            miny = min(p[stl.Dimension.Y], miny)
            maxz = max(p[stl.Dimension.Z], maxz)
            minz = min(p[stl.Dimension.Z], minz)
    return minx, maxx, miny, maxy, minz, maxz



def get_center_xyz(main_body):
    minx, maxx, miny, maxy, minz, maxz = find_mins_maxs(main_body)

    minx=round(minx,3)
    maxx=round(maxx,3)
    miny=round(miny,3)
    maxy=round(maxy,3)
    minz=round(minz,3)
    maxz=round(maxz,3)

    xsize = round(maxx-minx,3)
    ysize = round(maxy-miny,3)
    zsize = round(maxz-minz,3)

    midx = round(xsize/2,3)
    midy = round(ysize/2,3)
    midz = round(zsize/2,3)

    ctrx = round(-minx+(-midx),4)
    ctry = round(-miny+(-midy),4)
    ctrz = round(-minz+(-midz),4)

    return (ctrx, ctry, -minz)



