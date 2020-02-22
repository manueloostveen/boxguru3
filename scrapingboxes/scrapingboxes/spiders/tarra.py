# -*- coding: utf-8 -*-
import scrapy
from scrapingboxes.scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.scrapingboxes.helpers import ItemUpdater2, TableHandler, PriceHandler2, all_text_from_elements
import re


class TableHandlerTarra(TableHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiple_inner_dimensions_words = []
        self.multiple_outer_dimensions_words = ['buitenmaat']
        self.measurement_words = []
        self.diameter_words = []
        self.standard_size_words = []
        self.bundle_words = ['minimale afname']
        self.outer_dimension_words = []
        self.variable_dimension_words_MIN = []
        self.variable_dimension_words_MAX = []
        self.variable_dimension_words = self.variable_dimension_words_MIN + self.variable_dimension_words_MAX
        self.color_words = []
        self.wall_thickness_words = ['aantal lagen']

        # words that can be used to skip certain header names
        self.skip_words = []
        self.create_indices_dict()


class ItemUpdaterTarra(ItemUpdater2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        new_wall_thickness_dict = {} # {'website word': 'single/double/triple wall'}
        self.wall_thickness_dict = {**self.wall_thickness_dict, **new_wall_thickness_dict}


class TarraSpider(scrapy.Spider):
    name = 'tarra'
    allowed_domains = ['tarra-pack.nl']
    start_urls = [
        'https://tarra-pack.nl/dozen-karton/enkel-golf/?product_list_limit=30',
        'https://tarra-pack.nl/dozen-karton/vouwdozen-dubbel-golfkarton/?product_list_limit=30',
        'https://tarra-pack.nl/alle-verzendverpakkingen?product_list_limit=30'
    ]

    def parse(self, response):
        product_links = response.xpath('//a[@class="product-item-link"]/@href').getall()
        for link in product_links:
            yield response.follow(link, self.parse_box)

        next_page = response.xpath('//a[@class="link  next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)


    def parse_box(self, response):
        box = ScrapingboxesItem()
        box_data = ItemUpdaterTarra(item=box, measured_in='mm')
        box_data.update_item(
            'description', 'all_inner_dimensions', 'tags', 'standard_size', 'product_type', 'color',
            text_element=response.xpath('//h1/span/text()')
        )

        table_handler = TableHandlerTarra(
            text_elements=response.xpath('//*[@class="product attribute description"]//p[1]/text()')
        )

        box_data.analyse_table_rows(
            string_list=response.xpath('//*[@class="product attribute description"]//p[1]/text()').getall(),
            table_handler=table_handler
        )

        price_handler = PriceHandler2(item=box)

        price_handler.create_price_table(
            tier_elements=response.xpath('//li[@class="item"]'),
            price_elements=response.xpath('//li[@class="item"]//span[@data-label="Excl. BTW"]')
        )

        price_handler.get_base_price_from_price_table()
        #
        box['url'] = response.request.url
        box['company'] = 'Tarra-pack'

        yield box


