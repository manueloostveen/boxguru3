# -*- coding: utf-8 -*-
import scrapy
import re

from scrapingboxes.scrapingboxes.utils import SeleniumRequest
from scrapingboxes.scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.scrapingboxes.helpers import ItemUpdater2, TableHandler, PriceHandler2




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
        new_wall_thickness_dict = {}  # {'website word': 'single/double/triple wall'}
        self.wall_thickness_dict = {**self.wall_thickness_dict, **new_wall_thickness_dict}


def get_bundle_size(text):
    bundle_pattern = re.compile(r'(?i)(\d*)\s(?:stuk|in\sdoos)')
    bundle_size = bundle_pattern.findall(text)
    if len(bundle_size) > 0:
        bundle_size = bundle_size[0]
        if bundle_size.isdigit():
            return int(bundle_size)
        elif bundle_size == "":
            return 1
    else:
        return None


class Kartonnendozen123Spider(scrapy.Spider):
    name = 'kartonnendozen123'
    allowed_domains = ['www.123kartonnendozen.nl']

    custom_settings = {
        "SELENIUM_DRIVER_ARGUMENTS": [],
        "DOWNLOADER_MIDDLEWARES": {"scrapingboxes.middlewares.SeleniumMiddleware": 80},
        # 'ITEM_PIPELINES': {'scrapingboxes.pipelines.TesterPipeline': 310},
        'DOWNLOAD_DELAY': 4,
    }

    def start_requests(self):
        start_urls = [
            'https://www.123kartonnendozen.nl/webwinkel/index.php?item=dozen-op-voorraad&action=page&group_id=81&lang=nl',
            'https://www.123kartonnendozen.nl/webwinkel/index.php?item=verzendverpakkingen&action=page&group_id=88&lang=nl'
        ]
        for link in start_urls:
            yield SeleniumRequest(url=link, callback=self.parse)

    def parse(self, response):
        category_links = response.xpath('//*[@class="pageProductlistdesc"]//a/@href').getall()
        for link in category_links:
            link = 'https://www.123kartonnendozen.nl' + link
            yield SeleniumRequest(url=link, callback=self.parse_category)

    def parse_category(self, response):
        product_links = response.xpath('//a[@class="article"]/@href').getall()
        for link in product_links:
            yield SeleniumRequest(url=link, callback=self.parse_box)

        next_page = response.xpath('//a[@class="listforward"]/@href').get()
        if next_page:
            yield SeleniumRequest(url=next_page, callback=self.parse_category)

    def parse_box(self, response):
        box = ScrapingboxesItem()
        box_data = ItemUpdaterTest(item=box, measured_in="mm")

        box_data.update_item(
            'description', 'all_inner_dimensions', 'tags', 'standard_size', 'product_type',
            description_element=response.xpath('//div[@class="detailcontainer"]//span[@itemprop="name"]')
        )
        #todo ItemUpdater pakt foute maten 'Brievenbuskoker met dop A3 - 330 x 30 mm - 100 stuks  Doos' => vardim 3.0 - 330

        box_data.update_item(
            'wall_thickness', 'color',
            description_element=response.xpath(
                '//div[@class="detailcontainer"]//span[@itemprop="description"]')
        )

        # determine bundle size
        text = response.xpath('//div[@class="detailcontainer"]//span[@itemprop="description"]/text()').get()
        text_alternative = response.xpath('//div[@class="detailcontainer"]//span[@itemprop="name"]/text()').get()
        bundle_pattern = re.compile(r'(?i)(\d*)\sstuk')
        bundle_size = bundle_pattern.findall(text)

        box['minimum_purchase'] = get_bundle_size(text)
        if not box['minimum_purchase']:
            box['minimum_purchase'] = get_bundle_size(text_alternative)
        if not box['minimum_purchase']:
            raise ValueError('No bundle size found', response.request.url)

        # price
        price_handler = PriceHandler2(item=box, price_multiplier=box['minimum_purchase'])
        price_handler.create_base_price_manually(
            price_element=response.xpath('//*[@class="pricecontainer"]//span[@itemprop="price"]')
        )

        # No staffelkorting
        box['price_table'] = {}

        box['url'] = response.request.url
        box['company'] = '123Kartonnendozen.nl'

        yield box
