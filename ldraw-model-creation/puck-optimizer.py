# hockey puck generator
# idea is to generate three circular layers, then go through the layers and 
# attempt to optimize them from 1x1 bricks to 1x2, 2x4 or 2x2 bricks
# if lucky, will hold together if built

# joadavis Nov 19, 2020

# LDraw uses a right-handed co-ordinate system where -Y is "up".
# LDraw units are 0.4mm approx. So a brick is 24 LDU tall and 20 LDU per side.



class LDrawPuckGen(object):
    # in LDU
    brick_height = 24
    brick_side = 20
    model = {}
    part_1x1 = "1x1"
    part_1x2 = "1x2"
    

    def generate_puck(self, diameter, height):
        # return a model represented by 3x3x3 dict structure
        # rendered parts will be bounded by the diameter
        radius = diameter/2        

        for h in range(height):
            for x in range(diameter):
                for z in range(diameter):
                    # TODO allow defining a different algorithm
                    if (radius-x)**2 + (radius-z)**2 < radius**2:
                        # model{x}{y}{z} = 1x1
                        # if sticking to a grid, can just hash together
                        # key = f"x{x}y{-h}z{z}"
                        key = f"{x} {-h} {z}"  # use spaces, easy to split
                        self.model[key] = self.part_1x1
        return self.model

    def optimize(self):
        # TODO optimize
        # return model structure after optimization
        return self.model

def create_file(model, filename):
    # creates a file containing a valid ldraw format for the model
    # example line: 1 4 10 -24 10 1 0 0 0 1 0 0 0 1 3005.dat
    # format:   1 <colour> x y z a b c d e f g h i <file>
    lines = []
    lines.append("0 // Created by puck-optimizer.py, joadavis\n")

    prefix_color_red = "1 4 "
    suffix_part1x1 = "3005.dat\n"
    suffix_part1x2 = "3004.dat\n"
    suffix_part2x2 = "3003.dat\n"
    suffix_part2x3 = "3002.dat\n"
    rotate_0 = " 1 0 0 0 1 0 0 0 1 "
    # rotate_90 = " 0 0 -1 0 1 0 1 0 0 "
    rotate_90 = " 0 0 1 0 1 0 -1 0 0 "

    for pos_key, part in model.items():
        # generate an output line for the part
        # TODO use a dict of part to partial line mappings incl. part orientation
        if part == LDrawPuckGen.part_1x1:
            # pull apart pos_key into x y z
            x, y, z = pos_key.split()

            suff = suffix_part1x1
            rot = rotate_0

            # adjust
            # look for possible matching neighbors to swap
            #nei_1x2 = x + " " + y + " " + str(int(z) + 1)
            nei_1x2 = str(int(x) + 1) + " " + y + " " + z
            print(nei_1x2)
            if nei_1x2 in model.keys() and y == "-2":
                # would like to del model[nei_1x2] but...
                model[nei_1x2] = "0"
                model[pos_key] = LDrawPuckGen.part_1x2
                suff = suffix_part1x2

            x = int(x) * LDrawPuckGen.brick_side
            y = int(y) * LDrawPuckGen.brick_height
            z = int(z) * LDrawPuckGen.brick_side
            lines.append(prefix_color_red + str(x) + " " + str(y) + " " + str(z) + rot + suff)
    # write lines to a file
    with open(filename, 'w') as f:
        #for eachline in lines:
        #    f.write(eachline + '\n')
        f.writelines(lines)
    



# first test - simple puck
diameter = 10
height = 3
filename = "./models/3layer-puck.ldr"

generator = LDrawPuckGen()

model = generator.generate_puck(diameter, height)
print(model)


#model = optimize(model)
generator.optimize()

create_file(generator.model, filename)


###
# found out unfortunately that parts are not rotated on a corner but rather positioned and based on the middle of the part
# so replacing two 1x1 with a 1x2 would need to go with half part placement based on the code above. :(

# possible unit tests
# diameter of 1 and height of 1 should just give 1 brick

