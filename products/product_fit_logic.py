# An product class that can be used to determine how to fit in
# a box
import math
#todo How palletizable is a box? Make a function that calculates the maximum boxes on
# a serface and then returns the percentage of area filled with box.

def determine_close_matching_boxes(box_object, required_rating):
    #todo finish determine close matching boxes function
    pass


def side_switch(side):
    """
    Helper function to easily switch to another side give a rectangle with
    a width and a length, using string input
    """
    assert side == "width" or side == "length", "wrong input for side_switch, must be 'width' or 'length'"

    if side == "width":
        return "length"

    return "width"


def product_fit(product, width, length, height):
    """
    helper function to determine if a Product object can fit once in a certain box or space
    """
    flag = False

    possible_orientations = []

    # volume check
    if product.volume() > width * length * height:
        return flag, possible_orientations

    # bottom box surface and height check
    for orientation in product.orientations():
        if product.get_value(orientation[0]) * product.get_value(orientation[1]) <= width * length:
            if product.get_value(orientation[0]) <= width and product.get_value(
                    orientation[1]) <= length and product.get_3rd_side_value(orientation) <= height:
                flag = True

                possible_orientations.append(orientation)
            elif product.get_value(orientation[1]) <= width and product.get_value(
                    orientation[0]) <= length and product.get_3rd_side_value(orientation) <= height:
                flag = True
                possible_orientations.append(orientation)
    print(flag)
    return flag, possible_orientations


def find_max_volume(list_of_boxes):
    """
    definition to determine one box in a list of boxes that has the largest volume
    :param list_of_boxes: list of lists with box dimensions
    :return: list with xyz box dimensions
    """
    largest_box = None
    largest_volume = float("-inf")

    for box in list_of_boxes:
        volume = box[0] * box[1] * box[2]
        if volume > largest_volume:
            largest_box = box
            largest_volume = volume

    return largest_box


class RectangularProduct:
    """
    Class for a product to be fit in a box
    """

    # TODO Add no_stacking variable to product requirements

    def __init__(self, width, length, height, no_tipping=False, no_stacking=False):
        """
        Initializes a three dimensional rectangular product. When no_tipping is True the only possible stacking
        orientation is width x length or "WL"
        :param width: width of product
        :param length: length of product
        :param height: height of product
        :param no_tipping: determines whether the product can be placed sideways
        """

        self._width = width
        self._length = length
        self._height = height
        self._volume = self._width * self._length * self._height

        # TODO: make width, length, height properties of the Object: https://docs.python.org/3/library/functions.html#int
        # TODO: implement an algorithm to create 'perfect' custom box

        # orientations with a dictionary to simplify input and computations
        if no_tipping:
            self._orientations = ["WL"]
        else:
            self._orientations = ["WL", "WH", "LH"]

        # dictionary to find the corresponding value of a side
        self._side_value_dict = {"W": self._width, "L": self._length, "H": self._height}

        # dictionary to find the 3rd side (or height) of a
        self._height_dictionary = {"WL": "H", "WH": "L", "LH": "W"}

        # yer or no stacking flag
        self._no_stacking = no_stacking

    def __str__(self):
        """
        returns a string representation of the product, all dimensions and its volume
        """
        return "Rectangular product, with dimensions: " + "\n" \
               + "Width: " + str(self._width) + "\n" \
               + "Length: " + str(self._length) + "\n" \
               + "Height: " + str(self._height) + "\n" \
               + "Volume: " + str(self._volume) + "\n"

    def orientations(self):
        """
        Generator that yields the different orientations of the product
        """
        for orientation in self._orientations:
            yield orientation

    def get_3rd_side_value(self, orientation):
        """
        helper method to give the value of the 3rd side or height of a give orientation,
        calls the initialized 3rd side dictionary
        """
        assert orientation in self._orientations, "Error, incorrect orientation input"
        return self.get_value(self._height_dictionary[orientation])

    def get_value(self, string):
        """
        Takes a string representation of a side or orientation and corresponding value
        """
        return self._side_value_dict[string]

    def max_in_length(self, orientation, length):
        """
        This helper method returns the maximum amount of products that can be placed next to a line with a given length.
        Orientations are strings: "WL" -> width * length, "WH" -> width * height, "LH" -> length * height
        The function tries to minimize the remaining space, in other words tries to maximize the amount of products.
        Returns list of strings that represent the possible orientations: e.g. ["WWWW", "WWWL", "WWLL"]
        """

        # computes the maximum amount of products by taking the smallest side of the orientation
        maximum_amount = int(length // self._side_value_dict[orientation[0]])
        if self._side_value_dict[orientation[0]] == self._side_value_dict[orientation[1]]:
            return [orientation[0] * maximum_amount]

        # computes all variations of the orientation that also results in maximum_amount_smallest
        orientations = []
        for rotations in range(maximum_amount + 1):

            if self._side_value_dict[orientation[0]] * (maximum_amount - rotations) + \
                    self._side_value_dict[orientation[1]] * rotations <= length:
                orientations.append(orientation[0] * (maximum_amount - rotations) + orientation[1] * rotations)
            else:
                break

        return orientations

    def orientations_on_side(self, orientation, length):
        """
        Determines all possible orientations of a rectangle placed on a line with a given length
        Orientations are strings: "WL" -> width * length, "WH" -> width * height, "LH" -> length * height
        returns a list of string representations, e.g.: ["WWW", "WL", "LL"]
        """
        # determines the maximum amount on the line taking the longest side of the orientation
        max_longest = int(length // self._side_value_dict[orientation[1]])

        orientations = []

        for rotation in range(max_longest + 1):
            long_sides = max_longest - rotation
            string = long_sides * orientation[1]
            remaining_length = length - (long_sides * self._side_value_dict[orientation[1]])
            max_shortest = int(remaining_length // self._side_value_dict[orientation[0]])
            string += (max_shortest * orientation[0])
            orientations.append(string)

        return orientations

    def max_in_rectangle(self, orientation, box_width, box_length):
        """
        determines the maximum amount of products that can be placed on the bottom of a box,
        given one of its possible orientations.
        Returns a tuple (max_number_of_products, "orientation").
        Should also determine the remaining space
        """

        # determine all the ways to stack from both sides
        orientation_dict = {"length": self.orientations_on_side(orientation, box_length),
                            "width": self.orientations_on_side(orientation, box_width)}

        # determine the maximum stacking solution stacked from length

        solutions = []

        for box_side in orientation_dict:

            if box_side == "width":
                other_side = box_length
            elif box_side == "length":
                other_side = box_width
            else:
                assert box_side in ("width", "length"), "wrong orientation input"

            for orientations in orientation_dict[box_side]:
                total = 0

                for product_side in orientations:

                    if product_side == orientation[0]:
                        stacked_amount = other_side // self._side_value_dict[orientation[1]]
                        total += stacked_amount
                    elif product_side == orientation[1]:
                        stacked_amount = other_side // self._side_value_dict[orientation[0]]
                        total += stacked_amount

                solutions.append((total, orientation, box_side, orientations))

        return max(solutions)

    def remaining_spaces(self, max_bottom, width, length):
        """
        Computes the three remaining spaces after maximum filling a rectangle
        Uses the side_switch helper function
        """
        side_dictionary = {"width": width, "length": length}

        stacked_side = max_bottom[2]
        other_side = side_switch(max_bottom[2])

        remaining_spaces = []

        # remaining_space_1, computes stacking side - all the products
        remaining_space_1 = [side_dictionary[stacked_side], side_dictionary[other_side]]
        for side in max_bottom[3]:
            remaining_space_1[0] -= self._side_value_dict[side]

        if remaining_space_1[0] and remaining_space_1[1] > 0:
            remaining_spaces.append(remaining_space_1)

        # remaining_space_2, computes space above short side oriented products (if any)
        remaining_space_2 = [max_bottom[3].count(max_bottom[1][0]) * self._side_value_dict[max_bottom[1][0]],
                             side_dictionary[other_side] - (
                                     side_dictionary[other_side] // self._side_value_dict[max_bottom[1][1]]) *
                             self._side_value_dict[max_bottom[1][1]]]
        if remaining_space_2[0] and remaining_space_2[1] > 0:
            remaining_spaces.append(remaining_space_2)

        # remaining_space_3, computes space above long side oriented products (if any)
        remaining_space_3 = [max_bottom[3].count(max_bottom[1][1]) * self._side_value_dict[max_bottom[1][1]],
                             side_dictionary[other_side] - (
                                     side_dictionary[other_side] // self._side_value_dict[max_bottom[1][0]]) *
                             self._side_value_dict[max_bottom[1][0]]]

        if remaining_space_3[0] and remaining_space_3[1] > 0:
            remaining_spaces.append(remaining_space_3)

        return remaining_spaces

    def product_fit(self, space_width, space_length, space_height):
        """
        Helper method to determine if the product can fit at least once in a give 3D space
        :param space_width: width of space
        :param space_length: length of space
        :param space_height: height of space
        :return: returns (True or False, remaining possible orientations)
        """

        # initializes list of orientations
        flag = False
        possible_orientations = []

        # volume check
        if self._volume > space_width * space_length * space_height:
            return flag, possible_orientations

        else:
            for orientation in self._orientations:

                if self._side_value_dict[orientation[0]] <= space_width and self._side_value_dict[
                    orientation[1]] <= space_length and self.get_3rd_side_value(orientation) <= space_height:
                    possible_orientations.append(orientation)
                    flag = True

                elif self._side_value_dict[orientation[1]] <= space_width and self._side_value_dict[
                    orientation[0]] <= space_length and self.get_3rd_side_value(orientation) <= space_height:
                    possible_orientations.append(orientation)
                    flag = True

        return flag, possible_orientations

    def max_in_box(self, box_width, box_length, box_height):
        """
        Method to find the maximum amount of products that fit a given box
        :param box_width: width of box
        :param box_length: length of box
        :param box_height: height of box
        :return: tuple with (best solution, all solutions)
        solution consist of (maximum amount, (amount on first layer, orientation of product bottom, side of the box
        where first row is stacked from, representation of the product side placed on the chosen box side), annotation
        that explains if there are any products stacked in remaining spaces)
        """

        # test if product fits
        possible_product_fits = self.product_fit(box_width, box_length, box_height)

        # base case for recursive use of function
        if not possible_product_fits[0]:
            return (0, ""), ""

        # recursive case
        else:
            max_bottom = []
            for orientation in possible_product_fits[1]:
                max_bottom.append(self.max_in_rectangle(orientation, box_width, box_length))

            solutions = []

            for possibility in max_bottom:
                # calculate amount of products when stacking upwards
                first_layer = possibility[0]

                if not self._no_stacking:
                    stacked_upwards = first_layer * (box_height // self.get_3rd_side_value(possibility[1]))
                else:
                    stacked_upwards = first_layer

                # check remaining spaces, and add if products fit
                remaining_spaces = self.remaining_spaces(possibility, box_width, box_length)

                extra_products_rem = 0
                for remaining_space in remaining_spaces:
                    extra = self.max_in_box(remaining_space[0], remaining_space[1], box_height)[0][0]
                    extra_products_rem += extra

                # determine remaining volume if stacking is allowed
                if not self._no_stacking:
                    remaining_height = box_height - (
                            box_height // self.get_3rd_side_value(possibility[1])) * self.get_3rd_side_value(
                        possibility[1])

                    # compute amount of product in remaining height
                    extra_products_height = self.max_in_box(box_width, box_length, remaining_height)[0][0]

                else:
                    extra_products_height = 0

                # adds annotation when extra products are added after stacking upwards
                annotation = ""

                if extra_products_rem:
                    annotation = "Extra products stuffed"

                if extra_products_height:
                    annotation += "Extra products top layer"

                total_products = extra_products_rem + stacked_upwards + extra_products_height
                solutions.append((total_products, possibility, annotation))

            best_solution = max(solutions)

            for solution in solutions:
                if solution[2] == '':
                    best_solution = solution
                    break

            return best_solution, solutions


class CylindricalProduct:

    def __init__(self, diameter, height, no_tipping=False):
        self._diameter = float(diameter)
        self._height = float(height)
        self._radius = diameter / 2.0
        self._volume = math.pi * self._radius ** 2 * self._height

        if no_tipping:
            self._orientations = ["WL"]
        else:
            self._orientations = ["WL", "WH", "HL"]

    def __str__(self):
        """
        :return: Returns a string representation of the object, gives it diameter, height and volume.
        """
        return "Cylindrical product, with dimensions: " + "\n" \
               + "Diameter: " + str(self._diameter) + "\n" \
               + "Height: " + str(self._height) + "\n" \
               + "Volume: " + str(self._volume) + "\n"

    def max_in_rect(self, width, length):
        """
        helper function to determine the maximum amount of the product in a rectangle
        :param width: width of rectangle
        :param length: length of rectangle
        :return: maximum amount of products in the given rectangle
        """

        answer = {}
        number_in_w = width // self._diameter
        number_in_l = length // self._diameter

        # 1.0 determine rectangular pattern
        answer["rectangular_amount"] = number_in_w * number_in_l

        # 2.0 determine triangular pattern

        # 2.1 stacking from WIDTH
        columns_in_length = (((length / self._radius) - 2) // math.sqrt(3)) + 1

        # = check if all columns can fit the same amount
        if (width // self._radius) % 2 == 1:
            # = number of radii is odd, therefor columns can all be maximum height
            answer["triangular_amount_width"] = columns_in_length * number_in_w

        elif (width // self._radius) % 2 == 0:
            # = we are dealing with short and long columns that need to be alternated
            amount_of_short_columns = columns_in_length // 2
            amount_of_tall_columns = columns_in_length - amount_of_short_columns
            answer["triangular_amount_width"] = (amount_of_short_columns * (number_in_w - 1)
                                                 + amount_of_tall_columns * number_in_w)

        # 2.2 stacking from LENGTH
        columns_in_width = (((width / self._radius) - 2) // math.sqrt(3)) + 1

        # = check if all columns can fit the same amount
        if (length // self._radius) % 2 == 1:
            # number of radii is odd, therefor columns can all be maximum height
            answer["triangular_amount_length"] = columns_in_width * number_in_l

        elif (length // self._radius) % 2 == 0:
            # we are dealing with short and long columns that need to be alternated
            amount_of_short_columns = columns_in_width // 2
            amount_of_tall_columns = columns_in_width - amount_of_short_columns
            answer["triangular_amount_length"] = (amount_of_short_columns * (number_in_l - 1)
                                                  + amount_of_tall_columns * number_in_l)

        # === determine combination stacking
        # == extra row stacked from WIDTH
        if length - (number_in_l * self._diameter) > self._radius * math.sqrt(3):
            answer['extra_stacked_width'] = answer['rectangular_amount'] + (number_in_w - 1)

        # = extra row stacked from LENGTH
        if width - (number_in_w * self._diameter) > self._radius * math.sqrt(3):
            answer['extra_stacked_height'] = answer['rectangular_amount'] + (number_in_l - 1)

        return max(answer.values()), answer

    def product_fit(self, width, length, height):
        """
        determine if the product can fit at least once in give three dimensional space
        :param width: width of space
        :param length: length of space
        :param height: height of space
        :return: true or false
        """

        if self._diameter <= width and self._diameter <= length and self._height <= height:
            return True

        if self._height <= length and self._diameter <= width and self._diameter <= height:
            return True

        if self._height <= width and self._diameter <= length and self._diameter <= height:
            return True

        return False

    def max_in_box_base(self, width, length, height):
        """
        calculates the base maximum amount of the product that fits within a box with given dimensions
        :param width: width of box
        :param length: length of box
        :param height: height of box
        :return: list of maximum amount of products to fit in three dimensional space, the side from which is stacked,
        remaining space
        """
        #todo Add no stacking option
        answer = []

        # 1. determine the possible orientations of the space that can be used. If the product is not allowed to tip,
        # only the bottom side of the space can be used as a stacking orientation

        box_orientations = {"WL": (width, length), "WH": (width, height), "HL": (length, height)}
        third_side_dictionary = {"WL": height, "WH": length, "HL": width}

        # 2. for every orientation, determine max in rectangle
        for orientation in self._orientations:
            width = box_orientations[orientation][0]
            length = box_orientations[orientation][1]
            max_in_rectangle = self.max_in_rect(width, length)
            # 3. for every maximum amount on a side, stack upwards in direction of remaining side
            third_side = third_side_dictionary[orientation]
            stack_height = third_side // self._height

            base_maximum_amount = stack_height * max_in_rectangle[0]

            # 4. calculate remaining space
            remaining_space = (box_orientations[orientation][0], box_orientations[orientation][1],
                               third_side_dictionary[orientation] - stack_height * self._height)

            # 5. create list of answers containing all base stacking sizes
            answer.append((base_maximum_amount, orientation, remaining_space))

        return answer

    def max_in_box(self, width, length, height):
        """
        method to determine the maximum amount of product to fit in a box. Uses the max_in_box_base method
        :param width: width of box
        :param length: length of box
        :param height: height of box
        :return: returns (maximum amount in box, result of base stacking method, extra stacked amount)
        """
        base_amounts = self.max_in_box_base(width, length, height)
        total_amounts = []

        for possibility in base_amounts:
            remaining_space = possibility[2]
            extra_stacked = self.max_in_box_base(remaining_space[0], remaining_space[1], remaining_space[2])
            extra_stacked_amount = max(extra_stacked)[0]
            total_amounts.append((extra_stacked_amount + possibility[0], possibility, extra_stacked_amount))

        # finding best option. The following makes sure that if it is possible to maximize the amount without
        # stacking in a remaining space, this option is chosen
        max_amount = float("-inf")
        stacked_amount = float("inf")
        best_option = None
        for possibility in total_amounts:
            if possibility[0] >= max_amount and possibility[2] < stacked_amount:
                max_amount = possibility[0]
                stacked_amount = possibility[2]
                best_option = possibility

        return best_option


class Container(RectangularProduct):
    """
    Subclass of product class. This class can be used to create a container with a given
    volume and has a method to determine the quantity of a given box that fits inside
    """

    def max_rectangular_objects_inside(self, box_width, box_length, box_height):
        """
        Returns the maximum amount of boxes to fit inside this container object
        Takes a box as a tuple with 3 dimensions (dim1, dim2, dim3)
        """
        object_to_fit_inside = RectangularProduct(box_width, box_length, box_height)

        max_boxes_inside = object_to_fit_inside.max_in_box(self._width, self._length, self._height)

        return max_boxes_inside


class StoringSurface(RectangularProduct):
    """
    Creates a Subclass of Product class, that can be used to determine how much products or boxes
    can fit within the limits of the storing surface
    """

    def __init__(self, width, length):
        RectangularProduct.__init__(self, width, length, height=0)

        self._width = width
        self._length = length
        self._height = 0


#Testing
if __name__ == "__main__":
    product = RectangularProduct(86, 112, 220, no_tipping=True)
    print(product.max_in_box(430, 310, 220))
