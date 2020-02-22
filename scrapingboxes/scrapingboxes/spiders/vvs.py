# -*- coding: utf-8 -*-
import scrapy
from scrapingboxes.scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.scrapingboxes.helpers import ItemUpdater2, TableHandler, PriceHandler2, all_text_from_elements
import re


class TableHandlerVvs(TableHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiple_inner_dimensions_words = []
        self.multiple_outer_dimensions_words = []
        self.measurement_words = []
        self.diameter_words = []
        self.standard_size_words = []
        self.bundle_words = ["inhoud"]
        self.outer_dimension_words = []
        self.variable_dimension_words_MIN = []
        self.variable_dimension_words_MAX = []
        self.variable_dimension_words = self.variable_dimension_words_MIN + self.variable_dimension_words_MAX
        self.color_words = ["kleur"]
        self.wall_thickness_words = ['kwaliteit']

        # words that can be used to skip certain header names
        self.skip_words = []
        self.create_indices_dict()


class ItemUpdaterVvs(ItemUpdater2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        new_wall_thickness_dict = {
            'e-golf': 'enkelgolf',
            'b-golf': 'enkelgolf',
            'eb-golf': 'dubbelgolf',
            'c-golf': 'enkelgolf',
            'bc-golf': 'dubbelgolf',
            'cb-golf': 'dubbelgolf',
            'f-golf': 'enkelgolf',
        }  # {'website word': 'single/double/triple wall'}
        self.wall_thickness_dict = {**self.wall_thickness_dict, **new_wall_thickness_dict}

        self.clean_characters_dict = {
            "": ["(", ")", "mm", "cm", "41 l"],
            "ø": ["ø "],
            " ": ["  ", ", "],
            "-": [" – ", " - ", ' - ', "– ", "- "],
            ".": [","],
            "nr.": ['nr. ']
        }
        self.max_dimension_number = 18

        self.excludable_measurements = [
            "my",
            "gr",
            "0701",
            'nr.'
        ]


    def check_extra_variable_dimensions_VVS(self, description_string):
        if "vulhoogte" in description_string:
            numbers = re.findall("\d*\.\d+|\d+", description_string)
            if len(numbers) == 1:
                number = float(numbers[0])
                if number > self.max_dimension_number:  # special VIV condition because of "flessen" amount in description
                    self.item["inner_variable_dimension_MAX"] = number * self.multiplier
            else:
                raise ValueError('Too many numbers found in description')

    def check_bottle_amount(self, description_string, item):
        if "fles" in description_string:
            numbers = re.findall("\d+", description_string)
            for number in numbers:
                if int(number) <= 18:
                    item['bottles'] = int(number)

class PriceHandlerVVS(PriceHandler2):
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
                regex_number = float(re.search("\d*\.\d+", clean_text).group()) / self.price_multiplier
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
                numbers = re.findall("\d+", tier_object)
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
            self.price_table = {tiers_cleaned[index]: prices_cleaned[index] for index in range(len(tiers_cleaned))}
        except IndexError:
            print("tiers_cleaned: ", tiers_cleaned, "prices_cleaned: ", prices_cleaned)
            raise IndexError

        self.item['price_table'] = self.price_table

        return self.price_table

class VvsSpider(scrapy.Spider):
    name = 'vvs'
    allowed_domains = ['www.verzendverpakkingenshop.nl']
    start_urls = [
        'https://www.verzendverpakkingenshop.nl/brievenbusdozen',
        'https://www.verzendverpakkingenshop.nl/kartonnen-dozen',
        'https://www.verzendverpakkingenshop.nl/enveloppen'
    ]

    def parse(self, response):
        product_links = response.xpath('//*[@class="product-item-info"]/div[1]/a/@href').getall()
        for link in product_links:
            yield response.follow(link, self.parse_box)

        next_page = response.xpath('//*[@class="action  next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_box(self, response):
        box = ScrapingboxesItem()

        #Todo Fix table handler results, some boxes have no dimensions: https://www.verzendverpakkingenshop.nl/boekverpakking-455x325-80mm-a3-wit-e-golf-plak-en-tearstrip
        table_handler = TableHandlerVvs(
            header_elements=response.xpath('//*[@class="product data items"]//tbody/tr/th')
        )
        box_data = ItemUpdaterVvs(item=box, measured_in="mm")

        box_data.update_item(
            'tags', 'description', 'standard_size', 'all_inner_dimensions', 'product_type',
            description_element=response.xpath('//h1/span')
        )

        # do bottle check
        box_data.check_bottle_amount(
            description_string=response.xpath('//h1/span/text()').get(),
            item=box
        )

        box_data.analyse_table_rows(
            row_elements=response.xpath('//*[@class="product data items"]//tbody/tr/td'),
            table_handler=table_handler
        )

        extra_description_string = response.xpath(
            '//*[@class="product data items"]//tbody/tr/td/text()[contains(., "vulhoogte")]')
        if extra_description_string:
            box_data.check_extra_variable_dimensions_VVS(
                description_string=extra_description_string.get()
            )

        price_handler = PriceHandlerVVS(item=box, price_multiplier=box['minimum_purchase'])

        box['price_ex_BTW'] = price_handler.create_base_price_manually(
            price_element=response.xpath('//div[@class="product-info-price"]//*[@data-label="Excl. btw"]')
        )

        tier_elements = response.xpath('//*[@class="prices-tier items"]/li/strong[1]')
        price_elements = response.xpath('//*[@class="prices-tier items"]/li/span[1]/span')
        if tier_elements and price_elements:
            box['price_table'] = price_handler.create_price_table(
                tier_elements=response.xpath('//*[@class="prices-tier items"]/li/strong[1]'),
                price_elements=response.xpath('//*[@class="prices-tier items"]/li/span[1]/span')
            )
        else:
            box['price_table'] = {}

        box['url'] = response.request.url
        box['company'] = 'Verzendverpakkingenshop.nl'

        # Product image
        # box['image_urls'] = response.xpath('//*[@class="fotorama__stage__shaft"]/div/img[1]/@src').get()

        yield box
