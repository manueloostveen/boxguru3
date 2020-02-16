# -*- coding: utf-8 -*-
import scrapy
from scrapingboxes.helpers import ItemUpdater2, PriceHandler2
from scrapingboxes.items import ScrapingboxesItem
import re


class ItemUpdaterPaardekooper(ItemUpdater2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_dimension_number = 18.0

        self.clean_characters_dict = {
            "": ["(", ")", "mm"],
            "ø": ["ø "],
            " ": ["  ", ", "],
            "-": [" – ", " - "],
            ".": [","],
        }

class PaardekooperSpider(scrapy.Spider):
    name = 'paardekooper'
    allowed_domains = ['www.paardekooper.nl']
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }
    start_urls = [
        'https://www.paardekooper.nl/nl_NL/industrie-dozen-en-bakken/2635/',
        'https://www.paardekooper.nl/nl_NL/industrie-verzendverpakkingen/2712/',
    ]

    def parse(self, response):
        for link in response.xpath("//*[@class='list-group sub-list']/a/@href").getall():
            yield response.follow(link, self.parse_category)

    def parse_category(self, response):
        for link in response.xpath("//*[@class='h4 article-title']/a/@href"):
            yield response.follow(link, self.parse_box)

        next_button_link = response.xpath("//*[@class='next']/a/@href").get()
        if next_button_link:
            yield response.follow(next_button_link, self.parse_category)

    def parse_box(self, response):
        box = ScrapingboxesItem()
        box_data = ItemUpdaterPaardekooper(item=box, measured_in="mm")

        # update item from product description
        box_data.update_item(
            'description', 'all_inner_dimensions', 'tags', 'standard_size', 'product_type', 'wall_thickness',
            description_element=response.xpath("//*[@class='section-title']")
        )

        # update minimum purchase/bundle size
        box_data.update_item(
            "minimum_purchase",
            description_element=response.xpath("//*[@itemprop='offers']/span/span")
        )

        # use PriceHandler
        price_handler = PriceHandler2(item=box, price_multiplier=box['minimum_purchase'])

        string_elements = response.xpath("//*[@class='quantity-event']/a")
        if string_elements:
            box['price_table'] = price_handler.create_price_table(
                string_elements=response.xpath("//*[@class='quantity-event']/a")
            )
        else:
            box['price_table'] = {}

        box['price_ex_BTW'] = price_handler.create_base_price_manually(
            price_element=response.xpath("//*[@itemprop='offers']/span[@class='price-sales']")
        )

        # add missing item attributes
        box['url'] = response.request.url
        box['company'] = "Paardekooper"

        yield box
