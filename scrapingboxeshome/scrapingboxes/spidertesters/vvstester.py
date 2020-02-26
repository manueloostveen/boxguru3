# -*- coding: utf-8 -*-
import scrapy
from scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.helpers import ItemUpdater, TableHandler, PriceHandler, all_text_from_elements


class TableHandlerTest(TableHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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

        # words that can be used to skip certain header names
        self.skip_words = ["onderstel", "tuimelklep"]
        self.create_indices_dict()


class ItemUpdaterTest(ItemUpdater):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class VvstesterSpider(scrapy.Spider):
    name = 'vvstester'
    allowed_domains = ['www.verzendverpakkingenshop.nl']
    start_urls = [
        'https://www.verzendverpakkingenshop.nl/brievenbusdozen',
        'https://www.verzendverpakkingenshop.nl/kartonnen-dozen',
        'https://www.verzendverpakkingenshop.nl/enveloppen'
    ]
    custom_settings = {
        'ITEM_PIPELINES': {'scrapingboxes.pipelines.TesterPipeline': 310},
    }

    def parse(self, response):
        product_links = response.xpath('//*[@class="product-item-info"]/div[1]/a/@href').getall()
        for link in product_links:
            yield response.follow(link, self.parse_box)

        next_page = response.xpath('//*[@class="action  next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_box(self, response):

        table_header_elements = response.xpath('//*[@class="product data items"]//tbody/tr/th/text()').getall()
        # for text in table_header_elements:
        #     yield {'test_field': text, 'url': response.request.url}

        table_row_elements = response.xpath('//*[@class="product data items"]//tbody/tr/td/text()').getall()
        for text in table_row_elements:
            yield {'test_field': text, 'url': response.request.url}

        price_element = None
        price_tier_elements = None
        price_tierprice_elements = None

        # yield {'test_field': None, 'url': response.request.url}
