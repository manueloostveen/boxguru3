# -*- coding: utf-8 -*-
import re

import scrapy

from scrapingboxes.scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.scrapingboxes.helpers import ItemUpdater2, TableHandler, PriceHandler, all_text_from_elements, PriceHandler2


def find_in_stock(description):
    if "op voorraad" in description:
        currently_in_stock = True
    else:
        currently_in_stock = False
    return currently_in_stock


class ItemUpdaterViv(ItemUpdater2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_dimension_number = 9.0
        self.wall_thickness_dict = {
            "enkel": "enkelgolf",
            "dubbel": "dubbelgolf",
            "driedubbel": "driedubbelgolf",
            'e-golf': 'enkelgolf',
        }


class TableHandlerViv(TableHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wall_thickness_words += ['kwaliteit']
        self.multiple_inner_dimensions_words += ["afmeting"]
        self.create_indices_dict()

class PriceHandlerViv(PriceHandler2):

    def create_price_table(self, tier_elements=None, price_elements=None, string_elements=None):
        tiers_cleaned = []
        prices_cleaned = []

        if string_elements and not tier_elements and not price_elements:
            string_list = all_text_from_elements(string_elements)

            for text in string_list:
                # finds the first number in the string if starts with number
                regex_number = int(re.search("^\d+", text).group()) * self.price_multiplier
                tiers_cleaned.append(regex_number)

            for text in string_list:
                clean_text = text.strip().replace(",", ".")
                regex_number = round(float(re.search("\d*\.\d+", clean_text).group()) / self.price_multiplier, 2)
                prices_cleaned.append(regex_number)

        elif tier_elements and price_elements and not string_elements:
            tier_object = all_text_from_elements(tier_elements)
            if isinstance(tier_object, list):
                for tier_text in tier_object:

                    # in case a range is given (e.g. "0-100')
                    numbers = re.findall("\d*\.\d+|\d+", tier_text)

                    if numbers:
                        if "-" in tier_text and len(numbers) == 1:
                            # based on rajapack tiers, where the first tier is "-100"
                            tiers_cleaned.append(1 * self.price_multiplier)
                        else:
                            try:
                                tiers_cleaned.append(int(numbers[0]) * self.price_multiplier)
                            except IndexError:
                                print(numbers)
                                raise IndexError("numbers: ", numbers)
                    else:
                        tiers_cleaned.append("null")

            else:
                numbers = re.findall("\d*\.\d+|\d+", tier_object)
                if numbers:
                    if "-" in tier_object and len(numbers) == 1:
                        # based on rajapack tiers, where the first tier is "-100"
                        tiers_cleaned.append(1 * self.price_multiplier)
                    else:
                        try:
                            tiers_cleaned.append(numbers[0] * self.price_multiplier)
                        except IndexError:
                            print(numbers)
                            raise IndexError("numbers: ", numbers)
                else:
                    tiers_cleaned.append("null")

            price_object = all_text_from_elements(price_elements)
            if isinstance(price_object, list):
                for price in price_object:
                    clean_price = price.strip().replace(",", ".")
                    try:
                        regex_number = re.search("\d*\.\d+", clean_price)
                        if regex_number:
                            price = round(float(regex_number.group()) / self.price_multiplier, 2)
                        else:
                            price = "null"
                        prices_cleaned.append(price)

                    except AttributeError:
                        print(price_object, price, clean_price)
                        raise AttributeError(price_object, price, clean_price)
            else:
                try:
                    clean_price = price_object.strip().replace(",", ".")
                    regex_number = re.search("\d*\.\d+", clean_price)
                    if regex_number:
                        price = round(float(regex_number.group()) / self.price_multiplier, 2)
                    else:
                        price = "null"
                    prices_cleaned.append(price)
                except AttributeError:
                    print(price_object)
                    raise AttributeError(price_object)


        else:
            raise ValueError("when tier_elements AND price_elements are selected "
                             "string_elements cannot be selected, and vice versa")

        try:
            # Divided by 121 and multiplied with 100 to get price ex BTW
            self.price_table = {tiers_cleaned[index]: round((prices_cleaned[index] / 121) * 100, 2) for index in range(len(tiers_cleaned))}
        except IndexError:
            print("tiers_cleaned: ", tiers_cleaned, "prices_cleaned: ", prices_cleaned)
            raise IndexError

        return self.price_table

class VivSpider(scrapy.Spider):
    name = "viv"
    allowed_domains = ["webshop.viv.nl"]
    start_urls = [
        "https://webshop.viv.nl/kartonnen-dozen/show/all",
        "https://webshop.viv.nl/verzendverpakkingen",
    ]

    def parse(self, response):
        for href in response.xpath("//h2/a/@href"):
            yield response.follow(href, callback=self.parse_box)

        for href in response.xpath('//*[@class="subcategories"]//@href'):
            yield response.follow(href, callback=self.parse)

    def parse_box(self, response):
        box = ScrapingboxesItem()

        in_stock_text = (
            response.xpath('//*[@id="product_addtocart_form"]/div[3]/img/@alt')
                .get()
                .lower()
        )
        box['in_stock'] = find_in_stock(in_stock_text)

        # retrieve prices and bundle size
        box_data = ItemUpdaterViv(item=box, measured_in="mm")

        box_data.update_item(
            'minimum_purchase',
            text_element=response.xpath('//*[@class="product-shop"]/text()[4]')
        )

        price_handler = PriceHandlerViv(box)

        box['price_ex_BTW'] = round((price_handler.create_base_price_manually(response.xpath(
            '//*/div[@class="product-view"]//*[@class="per-one"]//span[@class="price"]'
        )
        ) / 121 ) * 100, 2)


        box['price_table'] = price_handler.create_price_table(
            tier_elements=response.xpath("//*[@class='tier-prices product-pricing']/li"),
            price_elements=response.xpath("//*[@class='tier-prices product-pricing']/li/span[1]")
        )

        box['url'] = response.request.url

        # update item with product description
        product_description_text = response.xpath('//*[@id="product-name"]/h1/text()').get()

        box_data.update_item("tags", "description", "wall_thickness", "standard_size", 'product_type', 'bottles',
                             description_element=response.xpath('//*[@id="product-name"]/h1'))

        # analyse specs table
        indices_object = TableHandlerViv(
            header_elements=response.xpath('//tbody/tr/th')
        )

        box_data.analyse_table_rows(
            table_handler=indices_object,
            row_elements=response.xpath('//tbody/tr/td')
        )

        # indices_dict for testing purposes
        box[
            'indices_dict'] = indices_object.indices_dict, indices_object.multiple_inner_dimensions_words, indices_object.column_names
        box['company'] = 'Verpakkingsindustrie Veenendaal'

        # Product image
        box['image_urls'] = [response.xpath('//p[@class="product-image"]/a/img/@src').get()]

        yield box
