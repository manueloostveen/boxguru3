import re
from collections import defaultdict, OrderedDict


def get_measurements_from_description(string):
    # this finds all range numbers with [/|-]. E.g. 40 x 30 x 1.0 - 14.0 cm, 10x230x10/14 cm
    range_numbers = re.findall(r'\d*\.*\d+\s*[-|/]\s*\d*\.*\d+', '40 x 30 x 1.0 - 14.0 cm')

    # todo: make an advanced regex that can get all types of measurements from product description
    pass


def word_checker(string, word_list):
    for word in word_list:
        if word in string:
            return word
    return None


def get_box_type_from_category(response):
    pass


def all_text_from_elements(selector_elements):
    """
    if selector list is given as input, a list of equal length containing items with all the text per element is returned
    if a single selector is given as input, a single string is returned containing all the text of the element
    :param selector_elements:
    :return:
    """
    if len(selector_elements) > 1:

        return [" ".join(element.xpath('.//text()').getall())
                if element.xpath('.//text()')
                else "null"
                for element
                in
                selector_elements]
    else:
        return " ".join(selector_elements[0].xpath('.//text()').getall())


class ItemUpdater:

    def __init__(self, item=None, measured_in=None):

        if item is None:
            raise ValueError("No ItemObject given as input")
        if measured_in is None:
            raise ValueError("measured_in not specified, input: 'mm' or 'cm'")

        self.product_description_raw = ""
        self.product_description_clean = []

        self.item = item

        self.multiplier_dict = {"mm": 1.0, "cm": 10.0}

        self.multiplier = self.multiplier_dict.get(measured_in)

        self.inner_dimensions_list = ["inner_dim1", "inner_dim2", "inner_dim3"]
        self.outer_dimensions_list = ["outer_dim1", "outer_dim2", "outer_dim3"]

        self.max_dimension_number = float("-inf")

        self.wall_thickness_dict = {
            "enkel": "single wall",
            "dubbel": "double wall",
            "driedubbel": "triple wall",
        }

        self.excludable_words = [
            "voor",
            "van",
            "tot",
            "vanaf",
            "per",
            "om",
            "bij",
            "naast",
            "met",
            "in",
            "aan",
            "af",
            "boven",
            "formaat",
            "en",
        ]

        self.excludable_measurements = [
            "my",
            "gr.",
            'grs.',
        ]

        self.color_dict = {
            "brown": ["bruin", "brown"],
            "white": ["wit", "white"],
            "silver": ["zilver", "silver"],
            "gray": ["grijs", "gray", 'taupe'],
            "black": ["zwart", "black"],
            "pink": ["rose", "pink"],
            "gold": ["goud", "gold"],
            "blue": ["blauw", "blue", ],
            "green": ['groen', "green"],
            "red": ['rood', 'red'],
            'yellow': ['geel', 'yellow'],
            "orange": ['oranje', 'orange'],
            "purple": ['paars', "purple"],
            'fuchsia': ['fuchsia'],

        }

        self.clean_characters_dict = {
            "": ["(", ")", "mm", "cm"],
            "ø": ["ø "],
            " ": ["  ", ", "],
            "-": [" – ", " - "],
            ".": [","],
        }

        self.bundle_size_words = [
            "stuk",
        ]

    def update_description(self, description_element=None, text_element=None):
        """
        takes either a description element, in which case all text is extracted
        or takes a specific text element: For example when data from an attribute is needed.
        :param description_element: xpath element out of which all text can be extracted
        :param text_element: specific element already pointing at the needed text (e.g. .xpath('element/element/text()[3]')
        :return:
        """

        if description_element:
            self.product_description_raw = all_text_from_elements(description_element)

        elif text_element:
            self.product_description_raw = text_element.get()

        if self.product_description_raw:
            self.product_description_clean = self.create_clean_split_description(self.product_description_raw)
        else:
            self.product_description_clean = ""

    def create_clean_split_description(self, description):
        description_lowercase = description.lower()

        # clean up useless characters #todo: no the function splits the string at every x, e.g. fixeerverpakking
        for new_character, current_characters in self.clean_characters_dict.items():
            for character in current_characters:
                description_lowercase = description_lowercase.replace(character, new_character)

        description_lowercase_split = re.split('(?<!\D)x|\s[x]\s|\s', description_lowercase)

        # clean up excludable words or sections
        # todo: this cannot be right, removes all words containing 'gr'
        for section in list(description_lowercase_split):

            for word in self.excludable_measurements:
                if word in section:
                    description_lowercase_split.remove(section)
                    break
            if section == "":
                description_lowercase_split.remove(section)

        return description_lowercase_split

    def analyse_table_rows(self, row_elements, table_handler):

        for argument, index_list in table_handler.indices_dict.items():
            for index in index_list:
                try:
                    element = row_elements[index]
                except IndexError:
                    print(argument, index_list, table_handler.indices_dict.items())
                    raise IndexError("index_list: ", index_list, "indices_dict: ", table_handler.indices_dict.items())

                try:
                    self.update_item(argument, description_element=element)
                except ValueError:
                    raise ValueError(argument, table_handler.indices_dict.items(),
                                     row_elements[index])

    def create_all_tags(self):
        tags = [
            section
            for section in list(self.product_description_clean)
            if len(section) > 1
               and section not in self.excludable_words
               and not self.number_test(section)
        ]

        if self.item.get('all_tags'):
            self.item['all_tags'] += tags
        else:
            self.item["all_tags"] = tags

    def number_test(self, string):
        if string.isdigit():
            return True
        else:
            for character in string:
                if character.isdigit():
                    return True
        return False

    def check_if_standard_size(self):
        for section in list(self.product_description_clean):
            regex_standard_size = re.search("[a-c]\d[+]|[a-c]\d", section)
            if regex_standard_size:
                standard_size = regex_standard_size.group()
                self.item["standard_size"] = standard_size
                self.product_description_clean.remove(section)
                break

    def check_normal_inner_dimensions(self):
        for section in list(self.product_description_clean):
            # find variable sizes, options are e.g. 100-200 and/or 100/200
            range_numbers = re.findall(r'\d*\.*\d+\s*[-|/]\s*\d*\.*\d+', section)

            if len(range_numbers) == 1:
                # one section of two numbers is found, the numbers are removed from section
                section_new = re.sub(r'\d*\.*\d+\s*[-|/]\s*\d*\.*\d+', "", section)

                numbers = re.findall(r'\d*\.\d+|\d+', range_numbers[0])
                range_number_list = sorted([float(number) for number in numbers])
                self.item["inner_variable_dimension_MIN"] = range_number_list[0] * self.multiplier
                self.item["inner_variable_dimension_MAX"] = range_number_list[1] * self.multiplier

            elif len(range_numbers) > 1:
                raise ValueError("Multiple range measurements found in description")
            else:
                section_new = section

            numbers = re.findall("\d*\.\d+|\d+", section_new)

            if len(numbers) == 1:
                number = float(numbers[0])
                if number > self.max_dimension_number:  # special VIV condition because of "flessen" amount in description
                    self.item[self.inner_dimensions_list.pop(0)] = number * self.multiplier
                else:
                    self.item["extra_dim"] = number
                self.product_description_clean.remove(section)

            else:
                for str_number in numbers:
                    number = float(str_number)
                    if number > self.max_dimension_number:  # special VIV condition because of "flessen" amount in description
                        try:
                            self.item[self.inner_dimensions_list.pop(0)] = number * self.multiplier
                        except IndexError:
                            raise IndexError('product_description_clean: ', self.product_description_clean, 'section: ',
                                             section)
                    else:
                        self.item["extra_dim"] = number

    def check_normal_outer_dimensions(self):
        for section in list(self.product_description_clean):
            numbers = re.findall("\d*\.\d+|\d+", section)
            if len(numbers) == 1:
                number = float(numbers[0])
                self.item[self.outer_dimensions_list.pop(0)] = number * self.multiplier
                self.product_description_clean.remove(section)
            else:
                for str_number in numbers:
                    number = float(str_number)
                    if number > self.max_dimension_number:  # special VIV condition because of "flessen" amount in description
                        self.item[self.outer_dimensions_list.pop(0)] = number * self.multiplier
                    else:
                        self.item["extra_dim"] = number

    def check_variable_inner_dimensions(self, item_key=None):
        description = list(self.product_description_clean)

        # case 1: a single number was given as input, it is already known
        if len(description) == 1 and item_key:
            regex_number = re.search("\d*\.\d+|\d+", description[0])
            if regex_number:
                number = regex_number.group()
                self.item[item_key] = float(number) * self.multiplier

        # case 2: a longer description is given containing multiple sections that need to be checked for "-"
        else:
            for section in description:
                if "-" in section and self.number_test(section):
                    numbers = re.findall("\d*\.\d+|\d+", section)
                    if len(numbers) == 2:
                        range_number_list = sorted([float(number) for number in numbers])
                        self.item["inner_variable_dimension_MIN"] = float(range_number_list[0]) * self.multiplier
                        self.item["inner_variable_dimension_MAX"] = float(range_number_list[1]) * self.multiplier
                        self.product_description_clean.remove(section)
                    else:
                        # todo: raise exception
                        pass

    def check_variable_outer_dimensions(self, item_key=None):
        description = list(self.product_description_clean)

        # case 1: a single number was given as input, it is already known
        if len(description) == 1 and item_key:
            regex_number = re.search("\d*\.\d+|\d+", description[0])
            if regex_number:
                number = regex_number.group()
                self.item[item_key] = float(number) * self.multiplier

        # case 2: a longer description is given containing multiple sections that need to be checked for "-"
        else:
            for section in list(self.product_description_clean):
                if "-" in section and self.number_test(section):
                    numbers = re.findall("\d*\.\d+|\d+", section)
                    if len(numbers) == 2:
                        self.item["outer_variable_dimension_MIN"] = float(numbers[0]) * self.multiplier
                        self.item["outer_variable_dimension_MAX"] = float(numbers[1]) * self.multiplier
                        self.product_description_clean.remove(section)

    def check_color(self, table=False):
        for section in list(self.product_description_clean):
            for return_color, words_to_check in self.color_dict.items():
                for word in words_to_check:
                    if word in section:
                        self.item["color"] = return_color
                        self.product_description_clean.remove(section)
                        return

    def check_wall_thickness(self):

        def color_in_section(section):
            for key in self.wall_thickness_dict.keys():
                if key in section:
                    return key
            return False

        for section in list(self.product_description_clean):
            if color_in_section(section):
                self.item["wall_thickness"] = self.wall_thickness_dict[color_in_section(section)]
                break

    def check_diameter(self):
        description = list(self.product_description_clean)

        # case 1: a single number was given as input, it is already known
        if len(description) == 1:
            regex_number = re.search("\d*\.\d+|\d+", description[0])
            if regex_number:
                number = regex_number.group()
                self.item["diameter"] = float(number) * self.multiplier

        # case 2: a longer description is given containing multiple sections that need to be checked for "ø"
        else:
            for section in description:
                if "ø" in section:
                    regex_number = re.search("\d*\.\d+|\d+", section)
                    if regex_number:
                        number = float(regex_number.group())
                        self.item["diameter"] = number * self.multiplier
                        self.product_description_clean.remove(section)

    def check_bundle_size(self):
        for section in list(self.product_description_clean):
            regex_bundle = re.search("\d*\.\d+|\d+", section)
            if regex_bundle:
                try:
                    number = int(regex_bundle.group())
                    self.item["minimum_purchase"] = number
                    self.product_description_clean.remove(section)
                except:
                    raise ValueError("raw description:", self.product_description_raw)

        if not self.item.get('minimum_purchase'):
            self.item["minimum_purchase"] = 1

    def check_all_inner_dimensions(self, table=False):
        self.check_variable_inner_dimensions()
        self.check_normal_inner_dimensions()

    def check_all_outer_dimensions(self, table=False):
        self.check_variable_outer_dimensions()
        self.check_normal_outer_dimensions()

    def create_product_description(self):
        self.item["description"] = self.product_description_raw

    def update_item(self, *args, description_element=None, text_element=None):
        self.update_description(description_element=description_element, text_element=text_element)

        check_dict = {
            # manual attributes, not returned by BoxTableIndices object dictionary
            "tags": self.create_all_tags,
            "description": self.create_product_description,

            # attributes returned by BoxTableIndices object dictionary
            "standard_size": self.check_if_standard_size,
            "diameter": self.check_diameter,
            "all_inner_dimensions": self.check_all_inner_dimensions,
            "single_inner_dimensions": self.check_normal_inner_dimensions,
            "all_outer_dimensions": self.check_all_outer_dimensions,
            "single_outer_dimensions": self.check_normal_outer_dimensions,
            "inner_variable_dimension_MIN": self.check_variable_inner_dimensions,
            "inner_variable_dimension_MAX": self.check_variable_inner_dimensions,
            "outer_variable_dimension_MIN": self.check_variable_outer_dimensions,
            "outer_variable_dimension_MAX": self.check_variable_outer_dimensions,

            "minimum_purchase": self.check_bundle_size,
            "wall_thickness": self.check_wall_thickness,
            "color": self.check_color,
        }

        inner_var_dim_list = [
            "inner_variable_dimension_MIN",
            "inner_variable_dimension_MAX",
            "outer_variable_dimension_MIN",
            "outer_variable_dimension_MAX"
        ]

        if args:
            for arg in args:
                if word_checker(arg, inner_var_dim_list):
                    check_dict[arg](item_key=word_checker(arg, inner_var_dim_list))
                else:
                    check_dict[arg]()

            return self.item

        else:
            for key in check_dict.keys():
                if key == "all_outer_dimensions" or key == "single_outer_dimensions" or key == "minimum_purchase":
                    # do nothing
                    pass
                else:
                    if word_checker(key, inner_var_dim_list):
                        check_dict[key](item_key=word_checker(key, inner_var_dim_list))
                    else:
                        check_dict[key]()
            return self.item


class TableHandler:

    def __init__(self, header_elements=None, text_elements=None):
        self.indices_dict = defaultdict(list)

        self.header_elements = None
        self.header_text_elements = None

        if header_elements:
            self.header_elements = header_elements
        elif text_elements:
            self.header_text_elements = text_elements
        else:
            raise ValueError("No header_elements given as input")

        # words that are used to check column header
        self.multiple_inner_dimensions_words = ["binnenmaten"]
        self.multiple_outer_dimensions_words = ["buitenmaten"]
        self.measurement_words = ['lengte', 'breedte', 'hoogte']
        self.diameter_words = ["diameter"]
        self.standard_size_words = ["formaat"]
        self.bundle_words = ["pak"]
        self.outer_dimension_words = ["buiten", "bodem", "deksel"]
        self.variable_dimension_words_MIN = ["min"]
        self.variable_dimension_words_MAX = ["max"]
        self.variable_dimension_words = self.variable_dimension_words_MIN + self.variable_dimension_words_MAX
        self.color_words = ["kleur", "color"]
        self.wall_thickness_words = []
        self.bottles_words = ['flessen']

        # words that can be used to skip certain header names
        self.skip_words = ["onderstel", "tuimelklep"]

        self.measurement_unit = "cm"


        # # initialize indices dictionary
        # self.create_indices_dict()

    def get_measurement_unit(self):
        if self.column_names:
            for column_name in self.column_names:
                if " mm" in column_name or "(mm" in column_name:
                    self.measurement_unit = "mm"
                elif " cm" in column_name or '(cm' in column_name:
                    self.measurement_unit = "cm"
            return self.measurement_unit
        else:
            raise ValueError("TableHandler does not have column_names yet; "
                             "create column names with create_indices_dict method")

    def word_checker(string, word_list):
        for word in word_list:
            if word in string:
                return True
        return False

    def return_attribute_boolean_dict(self, index):
        title = self.column_names[index]
        attribute_boolean_dictionary = {
            'bottles': word_checker(title, self.bottles_words),

            "all_inner_dimensions": word_checker(title, self.multiple_inner_dimensions_words),

            "all_outer_dimensions": word_checker(title, self.multiple_outer_dimensions_words),

            "single_inner_dimensions": word_checker(title, self.measurement_words)
                                       and not word_checker(title, self.skip_words)
                                       and not word_checker(title, self.variable_dimension_words)
                                       and not word_checker(title, self.outer_dimension_words),

            "single_outer_dimensions": word_checker(title, self.outer_dimension_words)
                                       and word_checker(title, self.measurement_words)
                                       and not word_checker(title, self.variable_dimension_words),

            "outer_variable_dimension_MIN": word_checker(title, self.variable_dimension_words_MIN)
                                            and word_checker(title, self.measurement_words)
                                            and word_checker(title, self.outer_dimension_words),

            "inner_variable_dimension_MIN": word_checker(title, self.variable_dimension_words_MIN)
                                            and word_checker(title, self.measurement_words)
                                            and not word_checker(title, self.outer_dimension_words),

            "outer_variable_dimension_MAX": word_checker(title, self.variable_dimension_words_MAX)
                                            and word_checker(title, self.measurement_words)
                                            and word_checker(title, self.outer_dimension_words),

            "inner_variable_dimension_MAX": word_checker(title, self.variable_dimension_words_MAX)
                                            and word_checker(title, self.measurement_words)
                                            and not word_checker(title, self.outer_dimension_words),

            "minimum_purchase": word_checker(title, self.bundle_words)
                                and not word_checker(title, self.skip_words),

            "standard_size": word_checker(title, self.standard_size_words),

            "color": word_checker(title, self.color_words),

            "diameter": word_checker(title, self.diameter_words),

            "wall_thickness": word_checker(title, self.wall_thickness_words),

        }
        return attribute_boolean_dictionary

    def check_all_column_names(self):
        def index_is_box_attribute(attribute_boolean_dictionary):
            for item_attribute in attribute_boolean_dictionary.keys():
                if attribute_boolean_dictionary[item_attribute]:
                    return item_attribute
            return False

        for index in list(self.start_indices):
            attribute_boolean_dictionary = self.return_attribute_boolean_dict(index)
            box_attribute = index_is_box_attribute(attribute_boolean_dictionary)
            if box_attribute:
                self.indices_dict[box_attribute].append(index)
                self.start_indices.remove(index)

    def create_indices_dict(self):
        """
        function creates column names and indices dictionary with index: item_attribute to item attributes,
        to be used by an ItemUpdater object
        """
        if self.header_elements:
            column_texts = all_text_from_elements(self.header_elements)
        elif self.header_text_elements:
            column_texts = self.header_text_elements.getall()

        self.column_names = [name.lower() for name in column_texts]

        self.start_indices = list(range(len(self.column_names)))

        self.check_all_column_names()
        self.get_measurement_unit()
        return self.indices_dict


class PriceHandler:
    # todo: make item input for PriceHandler
    def __init__(self, price_multiplier=1):
        self.price_multiplier = price_multiplier

    def create_price_table(self, tier_elements=None, price_elements=None, string_elements=None):
        tiers_cleaned = []
        prices_cleaned = []

        if string_elements and not tier_elements and not price_elements:
            string_list = all_text_from_elements(string_elements)

            for text in string_list:
                # finds the first number in the string if starts with number
                regex_number = int(re.search("^\d+", text).group()) * self.price_multiplier
                tiers_cleaned.append(regex_number)

            for text in string_list:
                clean_text = text.strip().replace(",", ".")
                regex_number = float(re.search("\d*\.\d+", clean_text).group()) / self.price_multiplier
                prices_cleaned.append(regex_number)

        elif tier_elements and price_elements and not string_elements:
            tier_object = all_text_from_elements(tier_elements)
            if isinstance(tier_object, list):
                for tier_text in tier_object:

                    # in case a range is given (e.g. "0-100')
                    numbers = re.findall("\d*\.\d+|\d+", tier_text)

                    if numbers:
                        if "-" in tier_text and len(numbers) == 1:
                            # based on rajapack tiers, where the first tier is "-100"
                            tiers_cleaned.append(1 * self.price_multiplier)
                        else:
                            try:
                                tiers_cleaned.append(int(numbers[0]) * self.price_multiplier)
                            except IndexError:
                                print(numbers)
                                raise IndexError("numbers: ", numbers)
                    else:
                        tiers_cleaned.append("null")

            else:
                numbers = re.findall("\d*\.\d+|\d+", tier_object)
                if numbers:
                    if "-" in tier_object and len(numbers) == 1:
                        # based on rajapack tiers, where the first tier is "-100"
                        tiers_cleaned.append(1 * self.price_multiplier)
                    else:
                        try:
                            tiers_cleaned.append(numbers[0] * self.price_multiplier)
                        except IndexError:
                            print(numbers)
                            raise IndexError("numbers: ", numbers)
                else:
                    tiers_cleaned.append("null")

            price_object = all_text_from_elements(price_elements)
            if isinstance(price_object, list):
                for price in price_object:
                    clean_price = price.strip().replace(",", ".")
                    try:
                        regex_number = re.search("\d*\.\d+", clean_price)
                        if regex_number:
                            price = float(regex_number.group()) / self.price_multiplier
                        else:
                            price = "null"
                        prices_cleaned.append(price)

                    except AttributeError:
                        print(price_object, price, clean_price)
                        raise AttributeError(price_object, price, clean_price)
            else:
                try:
                    clean_price = price_object.strip().replace(",", ".")
                    regex_number = re.search("\d*\.\d+", clean_price)
                    if regex_number:
                        price = float(regex_number.group()) / self.price_multiplier
                    else:
                        price = "null"
                    prices_cleaned.append(price)
                except AttributeError:
                    print(price_object, clean_price)
                    raise AttributeError(price_object, clean_price)


        else:
            raise ValueError("when tier_elements AND price_elements are selected "
                             "string_elements cannot be selected, and vice versa")

        try:
            self.price_table = {tiers_cleaned[index]: prices_cleaned[index] for index in range(len(tiers_cleaned)) if
                                prices_cleaned[index] != 'null'}
        except IndexError:
            print("tiers_cleaned: ", tiers_cleaned, "prices_cleaned: ", prices_cleaned)
            raise IndexError

        return self.price_table

    def create_base_price_manually(self, price_element):
        price_text = all_text_from_elements(price_element)
        if isinstance(price_text, str):
            clean_price = price_text.strip().replace(",", ".")
            regex_number = re.search("\d*\.\d+", clean_price)

            if regex_number:
                base_price = float(regex_number.group()) / self.price_multiplier
                self.base_price = base_price
            else:
                raise ValueError("No number found in element text")
        else:
            raise ValueError(f'Wrong type price input, type is {type(price_text)}. Should be string')

        return self.base_price

    def get_base_price_from_price_table(self):
        if self.price_table:
            return list(self.price_table.values())[0]
        else:
            raise ValueError("No price table has has been created yet")

    def create_price_table_from_strings(self, string_list):
        # todo: no longer needed, create price table has been updated
        tiers_cleaned = []
        for text in string_list:
            regex_number = int(re.search("^\d+", text).group()) * self.price_multiplier
            tiers_cleaned.append(regex_number)

        prices_cleaned = []
        for text in string_list:
            clean_text = text.strip().replace(",", ".")
            regex_number = float(re.search("\d*\.\d+", clean_text).group()) / self.price_multiplier
            prices_cleaned.append(regex_number)

        return {tiers_cleaned[index]: prices_cleaned[index] for index in range(len(tiers_cleaned))}


class PriceHandler2:
    # todo: make item input for PriceHandler
    def __init__(self, item, price_multiplier=1):
        self.price_multiplier = price_multiplier
        self.item = item

    def create_price_table(self, tier_elements=None, price_elements=None, string_elements=None):
        tiers_cleaned = []
        prices_cleaned = []

        if string_elements and not tier_elements and not price_elements:
            string_object = all_text_from_elements(string_elements)
            if isinstance(string_object, list):
                for text in string_object:
                    # finds the first number in the string if starts with number
                    try:
                        regex_number = int(re.search("\d+\s", text).group()) * self.price_multiplier
                        tiers_cleaned.append(regex_number)
                    except AttributeError:
                        raise AttributeError(text, string_object)

                for text in string_object:
                    clean_text = text.strip().replace(",", ".")
                    regex_number = round(float(re.search("\d*\.\d+", clean_text).group()), 2) / self.price_multiplier
                    prices_cleaned.append(regex_number)

            elif isinstance(string_object, str):
                regex_number = int(re.search("\d+\s", string_object).group()) * self.price_multiplier
                tiers_cleaned.append(regex_number)
                clean_text = string_object.strip().replace(",", ".")
                regex_number = round(float(re.search("\d*\.\d+", clean_text).group()) / self.price_multiplier, 2)
                prices_cleaned.append(regex_number)

        elif tier_elements and price_elements and not string_elements:
            tier_object = all_text_from_elements(tier_elements)

            if isinstance(tier_object, list):
                for tier_text in tier_object:

                    # in case a range is given (e.g. "0-100')
                    numbers = re.findall("\d+", tier_text)

                    if numbers:
                        if "-" in tier_text and len(numbers) == 1:
                            # based on rajapack tiers, where the first tier is "-100"
                            tiers_cleaned.append(1 * self.price_multiplier)
                        else:
                            try:
                                tiers_cleaned.append(int(numbers[0]) * self.price_multiplier)
                            except IndexError:
                                print(numbers)
                                raise IndexError("numbers: ", numbers)
                    else:
                        tiers_cleaned.append("null")

            else:
                numbers = re.findall("\d+\s", tier_object)
                if numbers:
                    if "-" in tier_object and len(numbers) == 1:
                        # based on rajapack tiers, where the first tier is "-100"
                        tiers_cleaned.append(1 * self.price_multiplier)
                    else:
                        try:
                            tiers_cleaned.append(numbers[0] * self.price_multiplier)
                        except IndexError:
                            print(numbers)
                            raise IndexError("numbers: ", numbers)
                else:
                    tiers_cleaned.append("null")

            price_object = all_text_from_elements(price_elements)
            if isinstance(price_object, list):
                for price in price_object:
                    clean_price = price.strip().replace(",", ".")
                    try:
                        regex_number = re.search("\d*\.\d+", clean_price)
                        if regex_number:
                            price = round(float(regex_number.group()) / self.price_multiplier, 2)
                        else:
                            price = "null"
                        prices_cleaned.append(price)

                    except AttributeError:
                        print(price_object, price, clean_price)
                        raise AttributeError(price_object, price, clean_price)
            else:
                try:
                    clean_price = price_object.strip().replace(",", ".")
                    regex_number = re.search("\d*\.\d+", clean_price)
                    if regex_number:
                        price = round(float(regex_number.group()) / self.price_multiplier, 2)
                    else:
                        price = "null"
                    prices_cleaned.append(price)
                except AttributeError:
                    print(price_object, clean_price)
                    raise AttributeError(price_object, clean_price)


        else:
            raise ValueError("when tier_elements AND price_elements are selected "
                             "string_elements cannot be selected, and vice versa")

        try:
            self.price_table = {tiers_cleaned[index]: prices_cleaned[index] for index in range(len(tiers_cleaned)) if
                                prices_cleaned[index] != 'null'}
        except IndexError:
            print("tiers_cleaned: ", tiers_cleaned, "prices_cleaned: ", prices_cleaned)
            raise IndexError

        self.item['price_table'] = self.price_table

        return self.price_table

    def create_base_price_manually(self, price_element):
        price_element = all_text_from_elements(price_element)
        if isinstance(price_element, str):
            clean_price = price_element.strip().replace(",", ".")
            regex_number = re.search("\d*\.\d+", clean_price)

            if regex_number:
                base_price = round(float(regex_number.group()) / self.price_multiplier, 2)
                self.base_price = base_price
            else:
                raise ValueError("No number found in element text")
        else:
            raise ValueError(f'Wrong type price input, type is {type(price_element)}. Should be string')

        self.item['price_ex_BTW'] = self.base_price
        return self.base_price

    def get_base_price_from_price_table(self):
        if self.price_table:
            for price in list(self.price_table.values()):
                if isinstance(price, float):
                    price = round(price, 2)
                    self.item['price_ex_BTW'] = price
                    return price
            ### CHANGE AFTER TUPAK
            # price = list(self.price_table.values())[0]
            # self.item['price_ex_BTW'] = round(price, 2)
            # return price
        else:
            raise ValueError("No price table has has been created yet")

    def create_price_table_from_strings(self, string_list):
        # todo: no longer needed, create price table has been updated
        tiers_cleaned = []
        for text in string_list:
            regex_number = int(re.search("^\d+", text).group()) * self.price_multiplier
            tiers_cleaned.append(regex_number)

        prices_cleaned = []
        for text in string_list:
            clean_text = text.strip().replace(",", ".")
            regex_number = round(float(re.search("\d*\.\d+", clean_text).group()) / self.price_multiplier, 2)
            prices_cleaned.append(regex_number)
        table = {tiers_cleaned[index]: prices_cleaned[index] for index in range(len(tiers_cleaned))}
        self.item['price_table'] = table
        return table


class ItemUpdater2:

    def __init__(self, item=None, measured_in=None):

        if item is None:
            raise ValueError("No ItemObject given as input")
        if measured_in is None:
            raise ValueError("measured_in not specified, input: 'mm' or 'cm'")

        self.item = item

        self.multiplier_dict = {"mm": 1.0, "cm": 10.0}

        self.multiplier = self.multiplier_dict.get(measured_in)

        self.inner_dimensions_list = ["inner_dim1", "inner_dim2", "inner_dim3"]
        self.outer_dimensions_list = ["outer_dim1", "outer_dim2", "outer_dim3"]

        self.max_dimension_number = float("-inf")

        self.wall_thickness_dict = {
            "enkel": "enkelgolf",
            "driedubbel": "driedubbelgolf",
            "dubbel": "dubbelgolf",
        }

        self.excludable_words = [
            "voor",
            "van",
            "tot",
            "vanaf",
            "per",
            "om",
            "bij",
            "naast",
            "met",
            "in",
            "aan",
            "af",
            "boven",
            "formaat",
            "en",
        ]

        self.color_dict = {
            "bruin": ["bruin", "brown"],
            "wit": ["wit", "white"],
            "zilver": ["zilver", "silver"],
            "grijs": ["grijs", "gray", 'taupe'],
            "zwart": ["zwart", "black"],
            "roze": ["rose", "pink", 'roze'],
            "goud": ["goud", "gold"],
            "blauw": ["blauw", "blue", ],
            "groen": ['groen', "green"],
            "rood": ['rood', 'red'],
            'geel': ['geel', 'yellow'],
            "oranje": ['oranje', 'orange'],
            "paars": ['paars', "purple"],
            'fuchsia': ['fuchsia'],

        }

        self.box_type_dict = {
            "kisten/bakken": ["kist", 'transportbak', 'bak'],
            'UN-dozen': ['un ', 'gevaarlijke'],
            # Dit waren 'feestelijke dozen'
            'geschenkdozen': ['geschenk'] + ['kerst', "feest", 'sinterklaas', 'sint'],
            "bierdozen": ["bier"],
            "wijndozen": ['fles', 'wijn'],
            'enveloppen van karton': ['kartonnen enveloppen', 'verzendenvelop massief', 'verzendenvelop e-golf'],
            'luchtkussen enveloppen': ['luchtkussen envelop', 'luchtkussenenvelop'],
            'paklijst enveloppen': ['paklijst'],
            'waterafstotende enveloppen': ['waterafstotende envelop'],
            'schuim enveloppen': ['foam envelop'],
            'standaard enveloppen': ['envelop'],
            'envelobox': ['envelobox'],
            'magneetdozen': ['magneet'],
            'verzend zakken': ['verzendzak', 'bag', 'zak'],
            'trapezium kokers': ['trapeze', 'trapezium koker'],
            'driekhoeks kokers': ['driehoek koker'],
            'vierkante kokers': ['vierkante kokers en dozen'],
            "ronde kokers": ['koker'],
            "dozen inserts": ['insert', 'flesinterieur', 'tray', 'interieurs'],
            "koeldozen": ['thermo', 'koel', 'isothermisch', 'cool'],
            "postdozen": ["post", "retour", 'kleding', 'geschenk', 'schoen', 'fefco 711', 'fefco 0713', 'fefco 713'],
            "kruiswikkel- & boekverpakkingen": ["wikkel", "draaipak", 'lp ', 'kalender', "book", 'boek'],
            "verhuisdozen": ["verhuis"],
            "autolockdozen": ["autolock", "montage", "automatisch", 'speedbox', 'zweedse bodem'],
            "pallet dozen": ['container', 'palletb', 'palletd'],
            "dekseldozen": ["deksel", "opberg", "deksel", "easypack", 'stropdas', 'paraat'],
            "archiefdozen": ["archief", 'ordner'],
            "brievenbusdozen": ["brievenbus", 'busbox'],
            "schuimdozen": ["schuim"],
            "fixeer- & zweefverpakkingen": ["fixeer", "fixatie", 'zweef', 'korrvu'],
            "feestelijke dozen": ['kerst', "feest", 'sinterklaas', 'sint'],
            "stansdozen": ['stans'],
            'gondeldoosjes': ['gondel'],
            'giftcard dozen': ['giftcard'],
            'schuifdozen': ['schuifdoos'],
            'magazijn doos': ['magazijn'],
            'kartonnen platen': ['platen', 'golfkarton (grijs)karton en papier'],
            # todo "karton" hier verwijderd, dat gaat ergesn fouten opeleveren# pas op: palletplaten, moet boven 'pallet box' blijven
            'standaard dozen': ['vouwdoos', 'doos', 'standaarddozen', 'dozen'] + ['varibox', 'variabele hoogte', 'hoogte verstelbaar'],
            'paraatdozen': ['paraat'],
            'opvulmateriaal': ['opvulmateriaal']
            #todo pluggen voor verzendkokers rajapack 'pluggen voor verzendkokers\
        }

    def update_description(self, description_element=None, text_element=None, string=None):
        """
        takes either a description element, in which case all text is extracted
        or takes a specific text element: For example when data from an attribute is needed.
        :param description_element: xpath element out of which all text can be extracted
        :param text_element: specific element already pointing at the needed text (e.g. .xpath('element/element/text()[3]')
        :return:
        """

        if description_element:
            self.product_description_raw = ''
            for text in description_element.xpath('.//text()').getall():
                self.product_description_raw += text

        elif text_element:
            self.product_description_raw = text_element.get()

        elif string:
            self.product_description_raw = string

        if self.product_description_raw:
            self.product_description_clean = self.create_clean_description()
        else:
            self.product_description_clean = ""

    def create_clean_description(self):
        """
        The functions removes all measurements ending with: my, gr, grs, gr, l/ltr/ltrs
        It than replaces all the ',' with '.' for later float creation
        :return:
        """
        measurement_pattern = re.compile(r'(?i)(\s*\d*\.*\d+\s*(?:grs*|my|l)\.*)')

        return measurement_pattern.sub('', self.product_description_raw).replace(',', '.').lower()

    def analyse_table_rows(self, row_elements=None, table_handler=None, string_list=None):

        for argument, index_list in table_handler.indices_dict.items():
            for index in index_list:
                if row_elements:
                    element = row_elements[index]
                    self.update_item(argument, description_element=element, table=True)
                elif string_list:
                    string = string_list[index]
                    self.update_item(argument, string=string, table=True)
                # except ValueError:
                #     raise ValueError(argument, table_handler.indices_dict.items(),
                #                      row_elements[index])

    def create_all_tags(self, table=False):
        word_pattern = re.compile(r"[a-z]{2,}")
        tags = word_pattern.findall(self.product_description_raw.lower())

        # clean up tags
        for tag in list(tags):
            if tag in self.excludable_words:
                tags.remove(tag)

        # if multiple descriptions are used to collect tags
        if self.item.get('all_tags'):
            self.item['all_tags'] += tags
        else:
            self.item["all_tags"] = tags

    def check_if_standard_size(self, table=False):
        standard_size_pattern = re.compile(r"(?i)[a-c]\d[+]*")
        standard_size = standard_size_pattern.search(self.product_description_raw)
        if standard_size:
            standard_size = standard_size.group()
            standard_size = standard_size.upper()
            self.item["standard_size"] = standard_size
            self.product_description_clean = standard_size_pattern.sub('', self.product_description_clean)

    def check_all_inner_dimensions(self, table=False):
        self.check_all_dimensions_regex(
            var_dim_MIN="inner_variable_dimension_MIN",
            var_dim_MAX='inner_variable_dimension_MAX',
            dimlist=self.inner_dimensions_list
        )

    def check_all_outer_dimensions(self, table=False):
        self.check_all_dimensions_regex(
            var_dim_MIN='outer_variable_dimension_MIN',
            var_dim_MAX='outer_variable_dimension_MAX',
            dimlist=self.outer_dimensions_list
        )

    def check_all_dimensions_regex(self, var_dim_MIN, var_dim_MAX, dimlist):

        description = self.product_description_clean
        # check description for measurement unit
        if 'cm' in description and 'mm' in description:
            self.multiplier = 10.0
        elif 'mm' in description:
            self.multiplier = 1.0
        elif 'cm' in description:
            self.multiplier = 10.0

        variable_dims_pattern = re.compile(r'[^a-zA-Z]\d*\s*[x×]*\s*(\d*\.*\d+)\s*[-/–]\s*(\d*\.*\d+)\b(?!x|\s*x)')
        normal_dims_pattern = re.compile(r'(?i)(\d*\.*\d+)\s*[x×]\s*(\d*\.*\d+)\s*[x×]\s*(\d*\.*\d+)')
        two_dims_pattern = re.compile(r'(?i)(\d*\.*\d+)\s*[x×]\s*(\d*\.*\d+)')
        bottles_pattern = re.compile(r'(?i)(\d+)\s+fles')
        diameter_pattern = re.compile(r'(?i)ø\s*(\d*\.*\d+)')
        remaining_number_pattern = re.compile(r'(?i)\s*[^a-zA-Z](\d*\.*\d+)')

        # todo Trapazium koker regex maken

        # check for variable dimensions
        variable_dimensions = variable_dims_pattern.findall(description)

        if len(variable_dimensions) > 0:
            variable_dimensions = sorted([float(dimension) for dimension in variable_dimensions[0]])
            description = re.sub(r'(\d*)(\s*[x×]*\s*\d*\.*\d+\s*[-|/]\s*\d*\.*\d+)', r'\g<1>', description)
            if len(variable_dimensions) == 2:
                self.item[var_dim_MIN] = variable_dimensions[0] * self.multiplier
                self.item[var_dim_MAX] = variable_dimensions[1] * self.multiplier
            else:
                raise ValueError("Something went wrong with var_dim regex the regex", variable_dimensions,
                                 self.product_description_clean)

        elif len(variable_dimensions) > 1:
            raise ValueError("Multiple range measurements found in description", variable_dimensions,
                             self.product_description_clean)

        # check for normal dimensions
        normal_dimensions = normal_dims_pattern.findall(description)

        if len(normal_dimensions) > 0:
            normal_dimensions = [dimension for dimension in normal_dimensions[0]]
            if len(normal_dimensions) == 3:
                for dimension in normal_dimensions:
                    self.item[dimlist.pop(0)] = float(dimension) * self.multiplier
                description = normal_dims_pattern.sub('', description)
            else:
                raise ValueError("Not 3 dimensions found with regex: ", normal_dimensions,
                                 self.product_description_clean)
        elif len(normal_dimensions) > 1:
            raise ValueError('Something went wrong with the triple dimensions regex', normal_dimensions,
                             self.product_description_clean)

        # check double dimensions product
        double_dimensions = two_dims_pattern.findall(description)
        if len(double_dimensions) > 0:
            # if multiple sets of double dimensions are found, only the first set will be taken into account
            double_dimensions = [dimension for dimension in double_dimensions[0]]

            if len(double_dimensions) == 2:
                for dimension in double_dimensions:
                    self.item[dimlist.pop(0)] = float(dimension) * self.multiplier
                description = normal_dims_pattern.sub('', description)
            else:
                raise ValueError('Something went wrong with the double dimensions regex', double_dimensions,
                                 self.product_description_clean)

        # check diameter
        diameter = diameter_pattern.findall(description)
        if len(diameter) > 0:
            self.item['diameter'] = float(diameter[0]) * self.multiplier
            description = diameter_pattern.sub('', description)

        elif len(diameter) > 1:
            raise ValueError('Multiple diameters found', diameter, self.product_description_clean)

        # check for bottle amount
        bottles = bottles_pattern.findall(description)
        if len(bottles) > 0:
            self.item['bottles'] = float(bottles[0])
            description = bottles_pattern.sub('', description)

        elif len(bottles) > 1:
            raise ValueError('Something went wrong with the bottles regex', bottles, self.product_description_clean)

        # check if 1 remaining number ADDED FOR TUPAK VARIABLE HEIGHT KOKERS
        if 'koker' in description:
            remaining_number = remaining_number_pattern.findall(description)
            if len(remaining_number) == 1:
                dimension = remaining_number[0]
                self.item[dimlist.pop(0)] = float(dimension) * self.multiplier

        self.remaining_description = description

    def check_single_dimension(self, dimlist=None, itemkey=None):
        dimensions = re.findall(r'\d*\.*\d+', self.product_description_clean)

        if len(dimensions) == 1:
            dimension = float(dimensions[0])
            if itemkey:
                if itemkey == 'minimum_purchase':
                    self.item[itemkey] = dimension
                else:
                    self.item[itemkey] = dimension * self.multiplier
            elif dimlist:
                self.item[dimlist.pop(0)] = dimension * self.multiplier
            else:
                raise ValueError('Neither dimlist nor itemkey where given as input (or have None value)')

        else:
            if itemkey == 'minimum_purchase':
                return None
            else:
                raise ValueError('Multiple or no dimensions in cell', dimensions, self.product_description_clean)

    def check_single_inner_dimension(self, table=False):
        self.check_single_dimension(self.inner_dimensions_list)

    def check_single_outer_dimension(self, table=False):
        self.check_single_dimension(self.outer_dimensions_list)

    def check_single_var_dim_in_MIN(self, table=False):
        self.check_single_dimension(itemkey="inner_variable_dimension_MIN")

    def check_single_var_dim_in_MAX(self, table=False):
        self.check_single_dimension(itemkey="inner_variable_dimension_MAX")

    def check_single_var_dim_out_MIN(self, table=False):
        self.check_single_dimension(itemkey="outer_variable_dimension_MIN")

    def check_single_var_dim_out_MAX(self, table=False):
        self.check_single_dimension(itemkey="outer_variable_dimension_MAX")

    def check_diameter(self, table=False):
        self.check_single_dimension(itemkey='diameter')

    def check_bottles(self, table=False):
        description = self.product_description_clean
        if table:
            bottles_pattern = re.compile(r'(?i)\d+')
        else:
            bottles_pattern = re.compile(r'(?i)(\d+)\s+fles')

        bottles = bottles_pattern.findall(description)
        if len(bottles) == 1:
            self.item['bottles'] = float(bottles[0])

        elif len(bottles) > 1:
            raise ValueError('Something went wrong with the bottles regex', bottles, self.product_description_clean)

    def check_color(self, table=False):
        def color_found(color, word_list):
            for word in word_list:
                if word in self.product_description_raw.lower():
                    return color
            return None

        for return_color, words_to_check in self.color_dict.items():
            found_color = color_found(return_color, words_to_check)
            if found_color:
                self.item['color'] = found_color

    def check_wall_thickness(self, table=False):
        for quality in self.wall_thickness_dict.keys():
            if quality in self.product_description_raw.lower():
                self.item['wall_thickness'] = self.wall_thickness_dict[quality]
                return

    def check_bundle_size(self, table=False):
        self.check_single_dimension(itemkey='minimum_purchase')
        if not self.item.get('minimum_purchase'):
            self.item["minimum_purchase"] = 1

    def create_product_description(self, table=False):
        self.item["description"] = self.product_description_raw

    def check_box_type(self, table=False):
        if self.item.get('product_type'):
            return
        else:
            def type_found(word_list):
                for word in word_list:
                    if word in self.product_description_clean:
                        return True

            for box_type, word_list in self.box_type_dict.items():
                if type_found(word_list):
                    self.item['product_type'] = box_type
                    break

    def update_item(self, *args, description_element=None, text_element=None, string=None, table=False):
        self.update_description(description_element=description_element, text_element=text_element, string=string)
        # todo, maybe fix this with kwargs=True/False, and execute functions when True

        item_attribute_dict = {
            # attributes that are often found in product description
            "tags": self.create_all_tags,
            "description": self.create_product_description,
            "all_inner_dimensions": self.check_all_inner_dimensions,
            "wall_thickness": self.check_wall_thickness,
            "color": self.check_color,
            "standard_size": self.check_if_standard_size,
            'product_type': self.check_box_type,
            'bottles': self.check_bottles,

            # attributes returned by BoxTableIndices object dictionary
            "all_outer_dimensions": self.check_all_outer_dimensions,
            "diameter": self.check_diameter,
            "single_inner_dimensions": self.check_single_inner_dimension,
            "single_outer_dimensions": self.check_single_outer_dimension,
            "inner_variable_dimension_MIN": self.check_single_var_dim_in_MIN,
            "inner_variable_dimension_MAX": self.check_single_var_dim_in_MAX,
            "outer_variable_dimension_MIN": self.check_single_var_dim_out_MIN,
            "outer_variable_dimension_MAX": self.check_single_var_dim_out_MAX,
            "minimum_purchase": self.check_bundle_size
        }

        if args:
            for attribute in args:
                if item_attribute_dict.get(attribute):
                    item_attribute_dict[attribute](table=table)
                else:
                    raise ValueError('Faulty attribute given as argument', attribute)

            return self.item

        else:
            raise ValueError('No item attributes given as arguments.')
