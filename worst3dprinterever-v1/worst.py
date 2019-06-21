__author__ = 'joadavis'

# worst 3d printer I can imagine

# to use, get a VRML .wrl file and put it on your system
# you can create a 3D object and export it to .wrl in SketchUp
# just be sure to turn off as many of the detail options as you can
# once you have the file, put the path into the infile value below
# That will produce a directory full of images
# print all the images, cut them along grid lines, stack according to order number.
# from there can either enjoy as a flipbook or go further and cut along image lines in each layer

import sys
import getopt
import os
import Image
import ImageDraw
import ImageFont

# some constants to get things rolling
# infile = "test.wrl"
#infile = "c:\\personal\\model data\\cube-13fig12.wrl"
#infile = "c:\\personal\\model data\\block-min.wrl"
#infile = "c:\\personal\\model data\\blockmessy.wrl"
#infile = "c:\\personal\\model data\\blockyprisms-noframe.wrl"
#infile = "c:\\personal\\model data\\blockcar.wrl"
infile = "c:\\personal\\model data\\myhouse3.wrl"
in_format = "VRML"    # future feature
outdir = os.curdir + os.sep + os.path.basename(infile) + os.sep

# assuming an 8.5x11 sheet of paper, and 2 inches for a reem of 500 sheets
# x in 11 direction, z in 8.5 direction
dpi = 250   # to match the 500 sheets in 2 inches for 20lb paper
# 8.5x11 / 2x3.5 -> 4x3

#desiredxinch = 3.5
desiredxinch = 2
desiredyinch = 2
desiredzinch = 2

desiredlimitpoint = [desiredxinch * dpi, desiredyinch * dpi, desiredzinch * dpi]

#persheetimagesx = 3   # 11 / 3.5 ish
persheetimagesx = 5   # 11 / 2 ish
persheetimagesz = 4   # 8.5 / 2 ish

imagespersheet = persheetimagesx * persheetimagesz
sheetsneeded = (desiredyinch * dpi) / imagespersheet
if ((desiredyinch * dpi) % imagespersheet) != 0:
    sheetsneeded += 1
bigimagexpixels = persheetimagesx * desiredxinch * dpi
bigimagezpixels = persheetimagesz * desiredzinch * dpi

# set way off so they will be overwritten with good values
maxpoint = [-1000.0, -1000.0, -1000.0]
minpoint = [1000.0, 1000.0, 1000.0]

ready_images = []


# represent a VRML Shape, and utils to convert it for our use
class Shape(object):
    def __init__(self):
        self.inputlines = []
        self.endpoints = []
        self.indexes = []
        self.orderedpoints = []

    def prettyprint(self):
        print self.inputlines
        if hasattr(self, 'endpoints'):
            print "endpoints"
            print self.endpoints
        print "indexes"
        print self.indexes
        if hasattr(self, 'orderedpoints'):
            print "ordered endpoints"
            print self.orderedpoints


def calc_ratios(minpoint, maxpoint):
    """Calculate ratios for scaling and moving the wrl to fit in the print area."""
    # we may get a wrl with a lowest corner negative or positive
    # goal is to figure out how to adjust so that corner is at origin, and come up with scaling ratios for each axis
    # to bring it within xyz * dpi
    print "minpoint===", minpoint
    # calculate our smallest dimension for the print area
    # use that dimension to calculate scale for model in all dimensions so it will fit
    # if I was a genious (sic), I'd figure in rotations to make it fit the best.
    # scalingdimension = 0
    # if desiredxinch < desiredyinch and desiredxinch < desiredzinch:
    #     print "x is tightest"
    #     scalingdimension = 0
    # elif desiredyinch < desiredzinch:
    #     print "y is tightest"
    #     scalingdimension = 1
    # else:
    #     print "z is tightest"
    #     scalingdimension = 2
    # print "range in scaling dimension ", maxpoint[scalingdimension] - minpoint[scalingdimension]
    # print "scaling ratio ", desiredlimitpoint[scalingdimension] / (maxpoint[scalingdimension] - minpoint[scalingdimension])
    # return desiredlimitpoint[scalingdimension] / (maxpoint[scalingdimension] - minpoint[scalingdimension])

    #oops, need to pick the dimension with the most constraint
    ratios = []
    for dim in range(3):
        ratios.append(desiredlimitpoint[dim] / (maxpoint[dim] - minpoint[dim]))
        print desiredlimitpoint[dim], " / ", (maxpoint[dim] - minpoint[dim]), " = ", ratios[dim]

    # pick the smallest ratio so it won't overflow in any direction
    if ratios[0] < ratios[1] and ratios[0] < ratios[2]:
        return ratios[0]
    elif ratios[1] < ratios[2]:
        return ratios[1]
    else:
        return ratios[2]


def calc_edgepoints_really(startpoint, endpoint):
    """Return a list of points along the line from start to end at y integer resolution."""
    print "really",
    resultpoints = []
    # all points are now scaled integers
    # want the range to be an absolute number of steps, so separate the sign
    yrange = abs(endpoint[1] - startpoint[1])
    ysign = 1
    if startpoint[1] > endpoint[1]:
        ysign = -1
    # could +1 so it includes start and end points, but let next line handle connecting point...
    if yrange == 0:
        print "flat"
        return [startpoint, endpoint]
    xstep = (endpoint[0] - startpoint[0]) / float(yrange)
    zstep = (endpoint[2] - startpoint[2]) / float(yrange)
    for step in range(1, yrange):
        resultpoints.append([
            startpoint[0] + int(xstep * step),
            startpoint[1] + step * ysign,
            startpoint[2] + int(zstep * step)
        ])
    print "really result", resultpoints
    return resultpoints


def calc_edgepoints():
    """Calculate all the points along each edge line, applying scaling and translation then finally rounding to integers.
    Could pass minpoint, shapes and scalingratio as param, but already have that available. :P
    """
    for faceshape in shapes:
        transcalepoints = []
        for origpoint in faceshape.endpoints:
            transcalepoints.append([
                int((origpoint[0] - minpoint[0]) * scalingratio),
                int((origpoint[1] - minpoint[1]) * scalingratio),
                int((origpoint[2] - minpoint[2]) * scalingratio)
            ])
        print "scaled endpoints", transcalepoints
        lastid = -2   # special code
        firstid = -2  # special code
        for idex in faceshape.indexes:
            if lastid == -2:
                lastid = idex
                firstid = idex
            elif idex == -1:
                # back to start
                print "indexloop", lastid, firstid
                #faceshape.orderedendpoints += calc_edgepoints_really(transcalepoints[lastid], transcalepoints[firstid])
                faceshape.orderedpoints.extend(calc_edgepoints_really(transcalepoints[lastid], transcalepoints[firstid]))
                firstid = -2
                lastid = -2
            else:
                print "index ok", lastid, idex
                #faceshape.orderedendpoints += calc_edgepoints_really(transcalepoints[lastid], transcalepoints[idex])
                faceshape.orderedpoints.extend(calc_edgepoints_really(transcalepoints[lastid], transcalepoints[idex]))
                lastid = idex
                #if firstid == -2:
                #    firstid = idex
        # to avoid duplicates, calc_edgepoints_really doesn't include endpoints, so add them now
        #faceshape.orderedpoints.extend(transcalepoints)
        # sort the points by y value
        print faceshape.orderedpoints
        #faceshape.orderedpoints = list(set(faceshape.orderedpoints))
        faceshape.orderedpoints.sort(key=lambda x: x[1])
        print faceshape.orderedpoints
    return "ok"


# Shape {
# appearance DEF COL_FrontColor Appearance {
# material Material { diffuseColor 1 1 1 }
# }
# geometry IndexedFaceSet {
# solid FALSE
# coord Coordinate {
# point [
# 1.359 4.254 0,
# 3.811 4.254 0,
# 3.811 3.263 0,
# 1.359 3.263 0,
# ]
# }
# coordIndex [
# 0
# 1
# 2
# 3
# -1
# ]
# }
# }
# want the result to be a list of faces, with each face being a structure of the shape above
# also would like the bounding box, so we can scale it appropriately
def read_vrml(filepath):
    """Read a given World file, parse its contents, and return a structure of data."""
    # read in data, looking for landmarks
    f = open(filepath, 'r')
    #inshape = False
    inpoints = False
    inindex = False
    curlylevel = 0
    lastpoint = -1000

    #assuming smallish wrl
    #maxpoint = [-1000.0, -1000.0, -1000.0]
    #minpoint = [1000.0, 1000.0, 1000.0]

    shapes = []   # to hold Shape objects
    for line in f:
        line = line.strip()
        #TODO select statement
        if line[0] == '#':
            # ignore
            print ".",
        #elif "Shape {" in line:
        #    inshape = True
        #    curlylevel = 1
        #elif inshape and "point " in line:
        elif "point [" in line:
            print "start points"
            current_shape = Shape()
            current_shape.inputlines.append(line)
            inpoints = True
        elif inpoints and line == "]":
            print "end points"
            current_shape.inputlines.append(line)
            inpoints = False
        elif inpoints:
            # trim the trailing comma if present
            line = line.rstrip(',')
            current_shape.inputlines.append(line)
            # parse point, converting to float
            thispoint = map(float, line.split())
            print thispoint
            current_shape.endpoints.append(thispoint)
            # take statistics - highest,lowest of each coordinates
            #lame way to do this
            for n in range(3):
                if thispoint[n] < minpoint[n]:
                    minpoint[n] = thispoint[n]
                if thispoint[n] > maxpoint[n]:
                    maxpoint[n] = thispoint[n]
        elif "coordIndex [" in line:
            print "start index"
            current_shape.inputlines.append(line)
            lastpoint = -1000
            inindex = True
        elif inindex and line == "]":
            print "end index"
            current_shape.inputlines.append(line)
            inindex = False
            # close out the shape?
            shapes.append(current_shape)
        elif inindex:
            current_shape.inputlines.append(line)
            # one site said commas are just whitespace
            line = line.replace(',', '')
            indies = map(int, line.split())
            current_shape.indexes += indies
            print indies
            # parse order
            if lastpoint < -1:
                lastpoint = line[0]
                startpoint = line[0]
            elif line == "-1":
                # line back to start
                print "go back"
                lastpoint = -1000
            else:
                # draw line from lastpoint to this point
                lastpoint = line

    f.close()
    # turn face data into list of lines that define this face, to be connected when rendered

    #print minpoint
    #print maxpoint

    map(Shape.prettyprint, shapes)
    return shapes


def print_usage():
    """How do you use this thing?"""
    print "worst.py -i <input> -o <output directory, default input name less extension> -s <number of sheets>"
    # TODO print a longer explanation
    sys.exit()


def image_init(startcount):
    """Create an image with the right dimensions and separate into numbered sub images"""
    testim = Image.new('RGB',
                       (int(bigimagexpixels), int(bigimagezpixels)),
                       (255, 255, 255))
    testdraw = ImageDraw.Draw(testim)
    testfont = ImageFont.truetype("arial.ttf", 28)
    for xline in range(1, persheetimagesx + 1):
        testdraw.line((0, dpi * desiredzinch * xline, bigimagexpixels, dpi * desiredzinch * xline), fill="OrangeRed")

    for zline in range(1, persheetimagesz + 1):
        testdraw.line((dpi * desiredxinch * zline, 0, dpi * desiredxinch * zline, bigimagezpixels), fill="OrangeRed")
    for xnum in range(persheetimagesx):
        for imgnum in range(persheetimagesz):
            testdraw.text((2 + dpi * desiredxinch * xnum, desiredlimitpoint[2] * (imgnum + 1) - 32),
                          str(startcount + (imgnum * persheetimagesx) + xnum), (0,0,0), font=testfont)
    #testim.show()
    del testdraw  # not sure if needed, as it just falls out of scope

    return testim


def render_connectedpoints(layerpoints):
    """Finally, connect all the points for this face at this layer in the image."""
    #print "layer", layerpoints
    # calculate where to draw on which sheet
    sheetnum = layerpoints[0][1] // imagespersheet
    #print "onto sheet", sheetnum
    layerdraw = ImageDraw.Draw(ready_images[sheetnum])
    xoffset = (layerpoints[0][1] % persheetimagesx) * desiredlimitpoint[0]
    zoffset = (layerpoints[0][1] // persheetimagesx) % persheetimagesz * desiredlimitpoint[2]
    if len(layerpoints) == 1:
        layerdraw.point([layerpoints[0][0] + xoffset, layerpoints[0][2] + zoffset])
    elif len(layerpoints) == 2:
        layerdraw.line([layerpoints[0][0] + xoffset, layerpoints[0][2] + zoffset,
                        layerpoints[1][0] + xoffset, layerpoints[1][2] + zoffset], fill="Black")
    else:
        # cool, list comprehension!
        polypoints = [(p[0] + xoffset, p[2] + zoffset) for p in layerpoints]
        #print polypoints
        #layerdraw.polygon([layerpoints[0][0] + xoffset, layerpoints[0][2] + zoffset,
        #                   layerpoints[1][0] + xoffset, layerpoints[1][2] + zoffset], fill="Red")
        # SteelBlue looks good too
        layerdraw.polygon(polypoints, fill="DarkKhaki")

    # number the image for verification
    #layerfont = ImageFont.truetype("arial.ttf", 28)
    # interesting, but wrong
    #layerdraw.text((layerpoints[0][0] + xoffset, layerpoints[0][2] + zoffset + (desiredzinch * dpi - 32)),
    #                      str(layerpoints[0][1]), (0,0,0), font=layerfont)
    # yes this is redundantly writing the number, but this is the 'worst', remember?
    #layerdraw.text((xoffset, zoffset + (desiredzinch * dpi - 32)),
    #               str(layerpoints[0][1]), (0,0,0), font=layerfont)


def render_shapes(shapes):
    for ashape in shapes:
        currenty = -1
        layerpoints = []
        for apoint in ashape.orderedpoints:
            if currenty == -1:
                currenty = apoint[1]
            if apoint[1] == currenty:
                layerpoints.append(apoint)
            else:
                # figure out which sheet to draw on at which position
                # this point is not on the layer, so put it in next layer
                render_connectedpoints(layerpoints)
                layerpoints = [apoint]
                currenty = apoint[1]
        # render the last layer
        render_connectedpoints(layerpoints)
        # side effects of function calls are updating the images :P


if __name__ == '__main__':
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "hi:o:s:")
    for opt, arg in opts:
        if opt == "-h":
            print_usage()
        elif opt == "-i":
            infile = arg
        elif opt == "-o":
            outdir = arg
        elif opt == "-s":
            sheetsneeded = arg
        else:
            print_usage()

        # TODO width, length, number of images per sheet, stuff like that

    print "expected sheets ", sheetsneeded
    shapes = read_vrml(infile)
    print "max ", maxpoint, " min ", minpoint
    scalingratio = calc_ratios(minpoint, maxpoint)
    print "scaling ", scalingratio
    calc_edgepoints()  # shapes, scalingratio)  #, minpoint)
    # initialize images (dpi * y inches) including image numbers
    # draw lines per layer from shape.edgepoints
    # composite images into pages, and write out

    for sheetnum in range(sheetsneeded):
        ready_images.append(image_init(imagespersheet * sheetnum + 1))
    render_shapes(shapes)

    ready_images[0].show()
    #ready_images[21].show()
    #ready_images[41].show()
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    for imnum in range(len(ready_images)):
        #ready_images[imnum].save("c:\\temp\\sheet" + str(imnum) + ".png", "PNG")
        ready_images[imnum].save(outdir + "sheet" + str(imnum) + ".png", "PNG")
