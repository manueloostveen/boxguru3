# -*- coding: utf-8 -*-
import scrapy
from scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.helpers import ItemUpdater2, TableHandler, PriceHandler, all_text_from_elements
import re

class TableHandlerTest(TableHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiple_inner_dimensions_words = []
        self.multiple_outer_dimensions_words = []
        self.measurement_words = []
        self.diameter_words = []
        self.standard_size_words = []
        self.bundle_words = []
        self.outer_dimension_words = []
        self.variable_dimension_words_MIN = []
        self.variable_dimension_words_MAX = []
        self.variable_dimension_words = self.variable_dimension_words_MIN + self.variable_dimension_words_MAX
        self.color_words = []
        self.wall_thickness_words = []

        # words that can be used to skip certain header names
        self.skip_words = []
        self.create_indices_dict()


class ItemUpdaterTest(ItemUpdater2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        new_wall_thickness_dict = {} # {'website word': 'single/double/triple wall'}
        self.wall_thickness_dict = {**self.wall_thickness_dict, **new_wall_thickness_dict}

class TestspiderSpider(scrapy.Spider):
    name = 'testspider'
    allowed_domains = ['www.test.nl']
    start_urls = ['www.test.nl']
    custom_settings = {'ITEM_PIPELINES':{'scrapingboxes.pipelines.TesterPipeline': 310}}

    def parse(self, response):
        pass

    def parse_box(self, response):
        box = ScrapingboxesItem()
        # table_handler = TableHandlerTest(header_elements=None)
        box_data = ItemUpdaterTest(item=box, measured_in="mm")
        price_handler = PriceHandler(price_multiplier=None)

        ## product description element test
        # product_description_element = None
        # yield {'test_field': product_description_element, 'url': response.request.url}

        # table header element test
        table_header_elements = response.xpath('/text()').getall()
        for text in table_header_elements:
            yield {'test_field': text, 'url': response.request.url}

        table_row_elements = None
        price_element = None
        price_tier_elements = None
        price_tierprice_elements = None

        yield {'test_field': None, 'url': response.request.url}



