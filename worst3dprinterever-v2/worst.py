__author__ = 'joadavis'

# worst 3d printer I can imagine

# History:
# The original idea was to create a 3D printer using a standard paper printer
# by slicing a model up in to images, and with a few parameters for size of
# print and the thickness of paper, produce many images that can be printed
# then manually cut and assembled (the "worst" part).

# See worst3dprinterever-v1 for older versions. The first version worked well
# with VRML .wrl files, until I realized SketchUp was in a 'trial' mode and
# I would soon no longer be able to export those.  I attempted a second version
# targeting the Collada .dae format, but hit many library issues.  The third
# version parses .stl files and attempts to make some output, but the result
# has a lot of extra shaded triangles.

# This is the "Version 2.0" as an attempt to make STL formats work well.

# Notes and References:
# Should try to make it easier on myself with some libraries
# There are many options for libraries:
# - https://pymesh.readthedocs.io/en/latest/ seems promising with other format support
# - https://buildmedia.readthedocs.org/media/pdf/python-stl/latest/python-stl.pdf no update since Nov17?
#   - https://python-stl.readthedocs.io/en/latest/
# - https://www.cs.cmu.edu/afs/cs/academic/class/15294u-s16/lectures/stl/stl.pdf
# - https://pypi.org/project/numpy-stl/ and https://numpy-stl.readthedocs.io/en/latest/
# - https://stackoverflow.com/questions/7566825/python-parsing-binary-stl-file -- a fair reference


# STL can be either a binary or ASCII format
# --> tinkercad export is binary
# reference from wikipedia:
# UINT8[80] – Header
# UINT32 – Number of triangles
#
# foreach triangle
# REAL32[3] – Normal vector
# REAL32[3] – Vertex 1
# REAL32[3] – Vertex 2
# REAL32[3] – Vertex 3
# UINT16 – Attribute byte count
# end

# terminology
# spi - sheets per inch of paper stack
# voxels - volume pixels, roughly

# options
# paper thickness - spi (sheets per inch)  For standard copier paper I estimated this at 250
# desired width and height and depth in inches?

# from desired dimensions, divide up 8.5x11 to get # images per sheet in x and z directions
# calculate the sheets needed from the (desired-height * spi) / persheetimagesx x persheetimagesy and round up
# calculate the number of voxels in x and z dir by persheetimagesx * desiredxinch * spi, same for z
# calculate min and max points to aid in centering model

# I'll take a quick stab at just parsing the binary file.
# struct seems pretty useful for this


import argparse
import os
import struct
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class STL_Shape(object):
    def __init__(self):
        self.header = ""
        self.num_triangles = 0
        self.triangles = []  # triangles can be a tuple with ((normal), (p1), (p2), (p3), attrib)
        self.min_point = [1000.0, 1000.0, 1000.0]   # hoping these are far enough out
        self.max_point = [-1000.0, -1000.0, -1000.0]
        self.scaling_ratio = 1
        self.transcale_triangles = []  # triangles that have been scaled and shifted into the "print area"
        self.sheet_images = []  # one image per sheet of paper

    def update_minmax(self, point):
        for coord in range(3):
            if point[coord] < self.min_point[coord]:
                self.min_point[coord] = point[coord]
            if point[coord] > self.max_point[coord]:
                self.max_point[coord] = point[coord]

    def calc_scaling_ratio(self, print_max_point):
        """Given a maximum point from 0 to contain the print,
        calculate a scaling ratio for use on all 3 dimensions
        max_point: distance from 0,0,0 that the print area
        contains
        :returns single float to use in scaling
        """
        ratios = []
        for dim in range(3):
            ratios.append(print_max_point[dim] / (self.max_point[dim] - self.min_point[dim]))
            if verbose > 0:
                print("limit {} / ({} - {}) gives ratio {}".format(
                    print_max_point[dim], self.max_point[dim], self.min_point[dim], ratios[dim]))
        # pick the smallest ratio so it won't overflow in any direction
        if ratios[0] < ratios[1] and ratios[0] < ratios[2]:
            self.scaling_ratio = ratios[0]
            return ratios[0]
        elif ratios[1] < ratios[2]:
            self.scaling_ratio = ratios[1]
            return ratios[1]
        else:
            self.scaling_ratio = ratios[2]
            return ratios[2]

    def render_triangles_to_images(self):
        if len(self.triangles) == 0:
            print("No triangles, can't render")
            raise Exception("no triangles to render")
        # create blank images

    def prettyprint(self):
        print("header: {}".format(self.header))
        print("number of triangles: {}".format(self.num_triangles))
        for tri in self.triangles:
            print("triangle data: {}".format(tri))
        print("min point {} max point {}".format(self.min_point, self.max_point))


def read_stl_bin(filepath):
    """"Read a binary STL file and break it up into triangles"""
    # got a lot of ideas from https://stackoverflow.com/questions/7566825/python-parsing-binary-stl-file

    shape_in = STL_Shape()

    with open(filepath, 'rb') as stlf:
        # header
        shape_in.header = stlf.read(80)
        print(shape_in.header)
        # number of triangles - 32bytes of integer
        shape_in.num_triangles = struct.unpack('@i', stlf.read(4))[0]
        print(shape_in.num_triangles)
        # each triangle
        for i in range(shape_in.num_triangles):
            normal_v = struct.unpack('<3f', stlf.read(12))
            if verbose > 0:
                print("normal to the triangle {}".format(normal_v))
            point1 = struct.unpack('<3f', stlf.read(12))
            point2 = struct.unpack('<3f', stlf.read(12))
            point3 = struct.unpack('<3f', stlf.read(12))
            shape_in.update_minmax(point1)
            shape_in.update_minmax(point2)
            shape_in.update_minmax(point3)
            if verbose > 1:
                print("points {} {} {}".format(point1, point2, point3))
            attrib = struct.unpack('<h', stlf.read(2))[0]
            if verbose > 2:
                print("attribute {}".format(attrib))
            shape_in.triangles.append((normal_v, point1, point2, point3, attrib))
        print("done reading")
    return shape_in


if __name__ == '__main__':
    # some defaults
    infile = "/home/joadavis/personal/model data/tinkercad/itsa_me.stl"
    out_dir = "./worst-run/"
    sheets_needed = 250  # default to an inch. a typical 20lb ream (500 sheets) of paper is 2 inches thick
    sheet_size_x = 10.5  # 11 inches minus a print margin
    sheet_size_z = 8     # 8.5 inches minus a print margin
    sheet_resolution = 250  # note 300dpi is a common printer resolution.  use this value for x and z
    verbose = 0

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    parser.add_argument("-i", "--in_file", type=str, help="The path to an input file (binary STL only)")
    parser.add_argument("-o", "--out_dir", type=str, help="output directory, "
                                                          "default is input name less extension")
    parser.add_argument("-p", "--pages_per_inch", type=int, default=250,
                        help="Number of pages stacked up to make an inch, related to the weight "
                             "of the paper used,"
                             " default is 250")
    parser.add_argument("-x", "--desired_x", type=float, default=1.0,
                        help="desired x width in inches, default is 1 inch")
    parser.add_argument("-y", "--desired_y", type=float, default=1.0,
                        help="desired y height in inches, default is 1 inch, "
                             "Note that this will be multiplied by p and divided by the "
                             "number of images on a sheet to determine how many sheets will be needed.")
    parser.add_argument("-z", "--desired_z", type=float, default=1.0,
                        help="desired z depth in inches, default is 1 inch")
    args = parser.parse_args()

    images_per_sheet = int(sheet_size_x / args.desired_x) * int(sheet_size_z / args.desired_z)
    sheets_needed = int(args.desired_y * args.pages_per_inch // images_per_sheet)
    if args.desired_y * args.pages_per_inch % images_per_sheet > 0:
        sheets_needed += 1
    print("Expect this to need {} sheets of paper with {} per sheet".format(sheets_needed, images_per_sheet))

    printarea_max_point = (args.desired_x * sheet_resolution,
                           sheets_needed * images_per_sheet, args.desired_y * sheet_resolution)
    print("Print area max point is {}".format(printarea_max_point))
    # something seems a little off here, but go for it

    if args.in_file:
        # TODO sanity checking of path
        infile = args.in_file
    # TODO check on outfile, default value, create path if needed
    if args.out_dir:
        out_dir = args.out_dir
    verbose = args.verbosity

    # temp - do something
    shape = read_stl_bin(infile)
    if verbose > 2:
        shape.prettyprint()

    # decide how the infile will fit in the print area
    print("winning scaling factor is {}".format(shape.calc_scaling_ratio(printarea_max_point)))

    shape.render_triangles_to_images()

    # last thing
    print("End run.")
