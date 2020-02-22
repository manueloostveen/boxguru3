# -*- coding: utf-8 -*-
import scrapy
import re
from scrapingboxes.scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.scrapingboxes.helpers import ItemUpdater2, TableHandler, PriceHandler2, all_text_from_elements

class TableHandlerPaco(TableHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiple_inner_dimensions_words = ["formaat"]
        self.multiple_outer_dimensions_words = []
        self.measurement_words = []
        self.diameter_words = []
        self.standard_size_words = []
        self.bundle_words = ['besteleenheid']
        self.outer_dimension_words = []
        self.variable_dimension_words_MIN = []
        self.variable_dimension_words_MAX = []
        self.variable_dimension_words = self.variable_dimension_words_MIN + self.variable_dimension_words_MAX
        self.color_words = ["kleur"]
        self.wall_thickness_words = ['materiaal']

        # words that can be used to skip certain header names
        self.skip_words = []
        self.create_indices_dict()


class ItemUpdaterPaco(ItemUpdater2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clean_characters_dict = {
            "": ["(", ")", "mm", "cm"],
            "ø": ["ø "],
            " ": ["  ", ", ", " - "],
            ".": [","],
            "/": [" / "]
        }

class PriceHandlerPaco(PriceHandler2):

    def create_price_table(self, tier_elements=None, price_elements=None, string_elements=None):
        tiers_cleaned = []
        prices_cleaned = []

        if string_elements and not tier_elements and not price_elements:
            string_list = all_text_from_elements(string_elements)

            for text in string_list:
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
                            tiers_cleaned.append(int(numbers[0]) * self.price_multiplier)
                        except IndexError:
                            print(numbers)
                            raise IndexError("numbers: ", numbers)
                else:
                    tiers_cleaned.append("null")

            price_object = all_text_from_elements(price_elements)
            if isinstance(price_object, list):
                ### DISCOUNT VERSION ### for pacoverpakkingen
                for price in price_object:
                    clean_price = price.strip().replace(",", ".")
                    try:
                        regex_number = re.search("\d+", clean_price)
                        if regex_number:
                            discount = float(regex_number.group())
                            price = (self.base_price / 100.0) * (100.0 - discount)
                        else:
                            price = "null"
                        prices_cleaned.append(price)

                    except AttributeError:
                        print(price_object, price, clean_price)
                        raise AttributeError(price_object, price, clean_price)
            else:
                clean_price = price_object.strip().replace(",", ".")

                try:
                    regex_number = re.search("\d+", clean_price)
                    if regex_number:
                        discount = float(regex_number.group())
                        price = (self.base_price / 100.0) * (100.0 - discount)
                    else:
                        price = "null"
                    prices_cleaned.append(price)
                except AttributeError:
                    print(price_object, clean_price)
                    raise AttributeError(price_object, clean_price)

        elif not tier_elements and not price_elements and not string_elements:
            #product has no tier discount
            pass

        else:
            raise ValueError("when tier_elements AND price_elements are selected "
                             "string_elements cannot be selected, and vice versa")

        try:
            self.price_table = {tiers_cleaned[index]: prices_cleaned[index] for index in range(len(tiers_cleaned))}
        except IndexError:
            print("tiers_cleaned: ", tiers_cleaned, "prices_cleaned: ", prices_cleaned)
            raise IndexError

        return self.price_table

class PacoverpakkingenSpider(scrapy.Spider):
    name = 'pacoverpakkingen'
    allowed_domains = ['www.pacoverpakkingen.nl']
    start_urls = ['https://www.pacoverpakkingen.nl/dozen/']

    def parse(self, response):
        # selectors
        product_links = response.xpath('//section[@id="products"]//div[@class="product-description "]//@href').getall()
        next_page = response.xpath('//a[@rel="next"]/@href').get()

        for link in product_links:
            yield response.follow(url=link, callback=self.parse_box)

        for times in range(16):
            yield response.follow(url=next_page, callback=self.parse)

    def parse_box(self, response):
        box = ScrapingboxesItem()
        table_handler = TableHandlerPaco(header_elements=response.xpath('//table[@class="featurestable"]//td[1]'))
        box_data = ItemUpdaterPaco(item=box, measured_in="cm")

        box_data.update_item(
            'description', 'tags', 'standard_size', 'product_type',
            description_element=response.xpath('//h1[@itemprop="name"]')
        )

        box_data.analyse_table_rows(
            row_elements=response.xpath('//table[@class="featurestable"]//td[2]'),
            table_handler=table_handler
        )

        price_handler = PriceHandlerPaco(item=box, price_multiplier=box['minimum_purchase'])

        box['price_ex_BTW'] = price_handler.create_base_price_manually(
            price_element=response.xpath('//div[@class="product-prices"]//*[@itemprop="price"]')
        )

        box['price_table'] = price_handler.create_price_table(
            tier_elements=response.xpath('//table[@class="table-product-discounts"]//tr[position() >1]/td[1]'),
            price_elements=response.xpath('//table[@class="table-product-discounts"]//tr[position() >1]/td[2]')
        )

        box['url'] = response.request.url
        box['company'] = 'PacoVerpakkingen'

        yield box



