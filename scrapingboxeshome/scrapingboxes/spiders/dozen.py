# -*- coding: utf-8 -*-
import scrapy

from scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.helpers import ItemUpdater2, TableHandler
import re

from scrapingboxes.settings import TestSettings
TESTING = TestSettings.TESTING

def create_price_table_dozenNL(string):
    """
    special function needed for dozen.nl price tiers. Hidden in html text
    :param string:
    :return:
    """
    clean_string = string.replace(",", ".")
    prices = re.findall("\d*\.\d+", clean_string)

    tiers = re.findall("(?<=[>])\d+", clean_string)
    if prices and tiers:
        return {int(tiers[index]): float(prices[index]) for index in range(len(tiers))}

    else:
        return None

class TableHandlerDozen(TableHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiple_inner_dimensions_words += ['binnenmaat']
        self.wall_thickness_words += ["kwaliteit"]
        self.bundle_words = ['per']
        self.create_indices_dict()

class ItemUpdaterDozen(ItemUpdater2):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        new_wall_thickness_dict = {"normaal": "enkelgolf",
                                   "medium": "dubbelgolf",
                                   "zwaar": "dubbelgolf"}
        self.wall_thickness_dict = {**self.wall_thickness_dict, **new_wall_thickness_dict}

class DozenSpider(scrapy.Spider):
    name = 'dozen'
    allowed_domains = ['www.dozen.nl']
    start_urls = ["https://www.dozen.nl/kartonnen-dozen/standaarddozen.html"]
    custom_settings = {}

    if TESTING:
        custom_settings = TestSettings.SETTINGS

    custom_settings['DOWNLOAD_DELAY'] = 1

    def parse(self, response):
        category_links = response.xpath("//*[@id='category-nav']/li/a/@href").getall()
        subcategory_links = response.xpath("//*[@id='category-nav']/li/ul/li/a/@href").getall()
        all_links = subcategory_links + category_links

        # add show all
        all_links_show_all = [link.replace(".html", "/show/all.html") for link in all_links]

        for idx, link in enumerate(all_links_show_all):
            if not "vulmateriaal" in link and not "tape" in link:
                if idx > TestSettings.MAX_ROWS and TESTING:
                    break
                yield response.follow(url=link, callback=self.parse_category)

    def parse_category(self, response):
        # check if page has products or needs to be skipped
        if response.xpath("//*[@class='from-price']").get():

            # iterate over table rows
            table_rows = response.xpath("//*[@class='table products-view']/tbody/tr")
            for idx, row in enumerate(table_rows):
                if idx > TestSettings.MAX_ROWS and TESTING:
                    break
                box = ScrapingboxesItem()
                box_data = ItemUpdaterDozen(item=box, measured_in="mm")
                header_indices_object = TableHandlerDozen(
                    header_elements=response.xpath("//thead/tr/th")
                )

                # analyse table rows
                box_data.analyse_table_rows(
                    table_handler=header_indices_object,
                    row_elements=row.xpath(".//td")
                )

                box['price_table'] = create_price_table_dozenNL(
                    string=row.xpath(".//*[@id='tierprices']/@data-content").get()
                )
                box['price_ex_BTW'] = box['price_table'][list(box['price_table'])[0]]

                # update box from page title
                box_data.update_item(
                    'description', 'tags', 'standard_size', 'product_type',
                    description_element=response.xpath("//*[@class='page-title category-title']/h1")
                )

                # extra info found in image alt attribute
                box_data.update_item(
                    "color",
                    "tags",
                    text_element=row.xpath('.//td[1]//@alt')
                )

                # create box url
                # example: https://www.dozen.nl/gekleurde-dozen/gekleurde-vouwdozen/breedte/155/hoogte/80/lengte/210.html
                if 'inner_dim3' in box:
                    box['url'] = response.request.url.replace("/show/all.html", f"/breedte/{int(box['inner_dim2'])}/hoogte/{int(box['inner_dim3'])}/lengte/{int(box['inner_dim1'])}.html")
                elif 'inner_variable_dimension_MIN' in box:
                    box['url'] = response.request.url.replace("/show/all.html", f"/breedte/{int(box['inner_dim2'])}/lengte/{int(box['inner_dim1'])}.html")
                else:
                    box['url'] = "error"

                box['company'] = "Dozen.nl"
                yield box


