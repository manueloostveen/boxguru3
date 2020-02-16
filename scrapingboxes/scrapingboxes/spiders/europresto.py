# -*- coding: utf-8 -*-
import scrapy

from scrapingboxes.utils import SeleniumRequest
from time import sleep
from scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.helpers import ItemUpdater2, TableHandler, PriceHandler
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, \
    ElementClickInterceptedException


# todo: make spider to also extract verzendkokers. They have missing dimension values in product description..

class ItemUpdaterEuropresto(ItemUpdater2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_dimension_number = 18.0

        self.clean_characters_dict = {
            "": ["(", ")", "- ", "mm"],
            "ø": ["ø "],
            " ": ["  ", ", "],
            "-": [" – ", " - "],
            ".": [","],
        }


class TableHandlerEuropresto(TableHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bundle_words = ["minimum"]
        self.create_indices_dict()


class EuroprestoSpider(scrapy.Spider):
    name = 'europresto'
    allowed_domains = ['www.europresto.nl']
    custom_settings = {
        "SELENIUM_DRIVER_ARGUMENTS": [
            # "--headless",
        ], "DOWNLOADER_MIDDLEWARES": {
            "scrapingboxes.middlewares.SeleniumMiddleware": 80,
        }
    }

    # todo: also extract verzendkokers

    def start_requests(self):
        url = "https://www.europresto.nl/catalogus/verpakkingen/dozen.html"
        yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):

        ###########################
        # https://stackoverflow.com/questions/24775988/how-to-navigate-to-a-new-webpage-in-selenium

        driver = response.request.meta['driver']

        # get box category links
        category_links = response.xpath(
            "//*[@class='catalog-button ']/a/@href"
        ).getall()

        for link in category_links:
            # go to category page
            driver.get(link)
            sleep(3)

            # click show more products button until impossible
            while True:
                try:
                    show_more_button = driver.find_element_by_xpath("//*[@id='showMoreLink']")
                    show_more_button.click()
                    sleep(5)
                except (ElementNotInteractableException, NoSuchElementException):
                    break
                except ElementClickInterceptedException:
                    pass

            # get box elements and links
            box_elements = driver.find_elements_by_xpath("//*[@class='hProduct name']/a")
            box_links = [box_elements[index].get_attribute('href') for index in range(len(box_elements))]

            for box_link in box_links:
                yield scrapy.Request(box_link, self.parse_box)

            # todo: add verzendkokers

    def parse_box(self, response):
        # initialize item
        box = ScrapingboxesItem()

        # create item data object
        box_data = ItemUpdaterEuropresto(item=box, measured_in="mm")

        # update from specifications
        header_indices_object = TableHandlerEuropresto(
            header_elements=response.xpath("//*[@class='specifics']/li")
        )

        box_data.analyse_table_rows(
            row_elements=response.xpath("//*[@class='specifics']/li/span"),
            table_handler=header_indices_object
        )

        # update from main title description
        box_data.update_item(
            'description', 'tags', 'all_inner_dimensions', 'standard_size', 'wall_thickness', 'product_type', 'color',
            description_element=response.xpath("//*[@class='product-description']/*/h1")
        )

        # use PriceHandler
        price_handler = PriceHandler()

        price_elements = response.xpath("//*[@class='bulk']/li/*[@class='price']")
        tier_elements = response.xpath("//*[@class='bulk']/li/*[@class='from']")
        if not price_elements or not tier_elements:
            box['price_table'] = {}
        else:
            box['price_table'] = price_handler.create_price_table(
                price_elements=response.xpath("//*[@class='bulk']/li/*[@class='price']"),
                tier_elements=response.xpath("//*[@class='bulk']/li/*[@class='from']")
            )

        box['price_ex_BTW'] = price_handler.create_base_price_manually(
            price_element=response.xpath("//*[@class='product-price']//*[@class='euro']")
        )

        # add missing item attributes
        box["url"] = response.request.url
        box["company"] = "Europresto"

        # for testing
        box["indices_dict"] = header_indices_object.indices_dict, header_indices_object.column_names
        yield box
