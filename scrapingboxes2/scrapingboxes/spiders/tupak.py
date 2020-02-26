# -*- coding: utf-8 -*-
import scrapy
from scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.helpers import ItemUpdater2, TableHandler, PriceHandler2


def check_url(url):
    skip_urls = ['folie', 'tape', 'opvul', 'maat']
    for word in skip_urls:
        if word in url:
            return False
    return True


class TableHandlerTupak(TableHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiple_inner_dimensions_words += ["afmetingen", 'lxbxh', 'lxb', 'diameter×lengte', 'bxlxh', 'bxl', 'binnen maat', 'lengte × breedte', 'diameter x inwendige lengte', 'Diameter x Inwendige lengte']
        self.multiple_outer_dimensions_words += ["uitwendig"]
        self.standard_size_words += ["geschikt"]
        self.bundle_words += ["bundel", "verpakkings­eenheid", 'doos-inhoud']
        self.measurement_words = []
        self.diameter_words = []
        self.create_indices_dict()

class ItemUpdaterTupak(ItemUpdater2):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

class PriceHanlderTupak(PriceHandler2):

    def get_base_price_from_price_table(self):
        if self.price_table:
            for price in list(self.price_table.values()):
                if type(price) == int:
                    self.item['price_ex_BTW'] = round(price, 2)
                    break

            return self.item['price_ex_BTW']
        else:
            raise ValueError("No price table has has been created yet")



class TupakSpider(scrapy.Spider):
    name = 'tupak'
    allowed_domains = ['www.tupak.com']
    start_urls = ["https://www.tupak.com/verpakkingsmateriaal/"]
    # start_urls = ['https://www.tupak.com/verpakkingsmateriaal/koker/kunststof/schroefkoker-verstelbaar?rv=1']

    def parse(self, response):

        if not response.xpath('//*/table'):
            # there is no product table on page
            # urls = response.xpath(
            #     '//*[@class="row body"]/*/ul[not(@class="menu-context") and not(@class="breadcrumbs")]/li/a/@href').getall()
            urls = response.xpath(
                '//body//@href').getall()
            for url in urls:
                if check_url(url):
                    yield response.follow(url=url, callback=self.parse)

        else:
            if response.request.url != "https://www.tupak.com/privacy-statement/":
                yield scrapy.Request(url=response.request.url, dont_filter=True, callback=self.parse_box)

    def parse_box(self, response):
            # iterate over different tables
            for box_table in response.xpath('//table'):

                boxes_rows = box_table.xpath('tbody/tr')
                for row in boxes_rows:
                    box = ScrapingboxesItem()
                    table = TableHandlerTupak(header_elements=box_table.xpath('thead/tr[@class="rij-2"][2]/th'))
                    box_data = ItemUpdater2(item=box, measured_in="mm")

                    # create data from product description
                    box_data.update_item(
                        "tags",
                        "color",
                        "wall_thickness",
                        "description",
                        'product_type',
                        description_element=response.xpath('//h1')
                    )

                    # iterate over row indices and update box
                    box_data.analyse_table_rows(
                        table_handler=table,
                        row_elements=row.xpath('td')
                    )

                    # create product url
                    relative_url = row.xpath('./td/a/@href').get()
                    if relative_url:
                        box["url"] = 'https://www.tupak.com' + relative_url
                    else:
                        box['url'] = response.request.url

                    # use PriceHandler
                    price_handler = PriceHandler2(item=box)
                    box["price_table"] = price_handler.create_price_table(
                        tier_elements=box_table.xpath('.//tr[@class="rij-2"][2]/th[@class="staffel"]'),
                        price_elements=row.xpath('./td[contains(@class, "prijs")]')
                    )

                    box['price_ex_BTW'] = price_handler.get_base_price_from_price_table()

                    # add item fields manually
                    box["company"] = 'Tupak'
                    box["in_stock"] = None
                    #
                    # # for testing
                    box["indices_dict"] = table.indices_dict

                    yield box
