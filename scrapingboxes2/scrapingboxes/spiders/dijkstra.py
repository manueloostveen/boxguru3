# -*- coding: utf-8 -*-
import scrapy
from scrapingboxes.items import ScrapingboxesItem

class DijkstraSpider(scrapy.Spider):
    name = 'dijkstra'
    allowed_domains = ['www.dijkstra.net']
    start_urls = ['https://www.dijkstra.net/verpakkingsglas/dranken']
    custom_settings = {
        'ITEM_PIPELINES': {

        }
    }

    def parse(self, response):
        products = response.xpath('//*[@class="product-item-link"]')

        for product in products:
            box = ScrapingboxesItem()
            description = product.xpath('./text()').get()
            box['description'] = description
            yield box


