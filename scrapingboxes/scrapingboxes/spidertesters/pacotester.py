# -*- coding: utf-8 -*-
import scrapy
from scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.helpers import ItemUpdater, TableHandler, PriceHandler

class TableHandlerTest(TableHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiple_inner_dimensions_words += []
        self.measurement_words += []
        self.standard_size_words += []
        self.skip_words += []
        self.create_indices_dict()


class ItemUpdaterTest(ItemUpdater):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class PacotesterSpider(scrapy.Spider):
    name = 'pacotester'
    allowed_domains = ['www.pacoverpakkingen.nl']
    start_urls = ['https://www.pacoverpakkingen.nl/dozen/']

    custom_settings = {'ITEM_PIPELINES':{'scrapingboxes.pipelines.TesterPipeline': 310}}


    def parse(self, response):
        # selectors
        product_links = response.xpath('//section[@id="products"]//div[@class="product-description "]//@href').getall()
        next_page = response.xpath('//a[@rel="next"]/@href').get()

        for link in product_links:
            yield response.follow(url=link, callback=self.parse_box)

        for times in range(16):
            yield response.follow(url=next_page, callback=self.parse)


    def parse_box(self, response):
        # selectors
        product_description = response.xpath('//h1[@itemprop="name"]/text()').get()
        header_text_list = response.xpath('//table[@class="featurestable"]//td[1]/text()').getall()



        # yield {'test_field': product_description}
        yield {'test_field': header_text_list, 'url': response.request.url}


