# -*- coding: utf-8 -*-
import re

import scrapy

from scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.helpers import ItemUpdater2, TableHandler, PriceHandler, PriceHandler2, all_text_from_elements
from scrapingboxes.settings import TestSettings

TESTING = TestSettings.TESTING


class TableHandlerRajapack(TableHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiple_inner_dimensions_words += ['voor ordner']
        self.measurement_words += ['opening', 'rug']
        self.standard_size_words += ['aanbevolen']
        self.skip_words += ["prijs"]
        self.bundle_words += ['(ve)']
        self.create_indices_dict()


class PriceHandlerRajapack(PriceHandler2):

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
                regex_number = float(re.search("\d*\.\d+", clean_text).group()) / self.price_multiplier
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
                        tiers_cleaned.append(1 * self.price_multiplier)

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
                    tiers_cleaned.append(1 * self.price_multiplier)

            price_object = all_text_from_elements(price_elements)
            if isinstance(price_object, list):
                for price in price_object:
                    clean_price = price.strip().replace(",", ".")
                    try:
                        regex_number = re.search("\d*\.\d+", clean_price)
                        if regex_number:
                            price = float(regex_number.group()) / self.price_multiplier
                        else:
                            price = 0
                        prices_cleaned.append(price)

                    except AttributeError:
                        print(price_object, price, clean_price)
                        raise AttributeError(price_object, price, clean_price)
            else:
                try:
                    clean_price = price_object.strip().replace(",", ".")
                    regex_number = re.search("\d*\.\d+", clean_price)
                    if regex_number:
                        price = float(regex_number.group()) / self.price_multiplier
                    else:
                        price = 0
                    prices_cleaned.append(price)
                except AttributeError:
                    print(price_object, clean_price)
                    raise AttributeError(price_object, clean_price)


        else:
            raise ValueError("when tier_elements AND price_elements are selected "
                             "string_elements cannot be selected, and vice versa")

        try:
            self.price_table = {tiers_cleaned[index]: prices_cleaned[index] for index in range(len(tiers_cleaned))}
        except IndexError:
            print("tiers_cleaned: ", tiers_cleaned, "prices_cleaned: ", prices_cleaned)
            raise IndexError

        return self.price_table


class RajapackSpider(scrapy.Spider):
    name = "rajapack"
    allowed_domains = ['www.rajapack.nl']
    if TESTING:
        custom_settings = TestSettings.SETTINGS

    start_urls = [
        'https://www.rajapack.nl/kartonnen-dozen-verzenddozen-exportcontainers/kartonnen-dozen_C1010.html',
        'https://www.rajapack.nl/kartonnen-dozen-verzenddozen-exportcontainers/postdozen-verzenddozen_C1040.html',
        'https://www.rajapack.nl/kartonnen-dozen-verzenddozen-exportcontainers/dozen-drukwerk_C1060.html',
        'https://www.rajapack.nl/kartonnen-dozen-verzenddozen-exportcontainers/dozen-met-speciale-afmetingen_C1020.html',
        'https://www.rajapack.nl/kartonnen-dozen-verzenddozen-exportcontainers/exportdozen-kisten_C1050.html',
        'https://www.rajapack.nl/promotionele-verpakkingen/flesverpakkingen_C1080.html',
        'https://www.rajapack.nl/kartonnen-dozen-verzenddozen-exportcontainers/dozen-gevaarlijke-producten_C1090.html',
        # todo ordner doos errors:
        #  "https://www.rajapack.nl/kartonnen-dozen-verzenddozen-exportcontainers/verhuisdozen-archivering/ordnerdoos-zelfklevende-sluiting_PDT01175.html"
        #  "https://www.rajapack.nl/kartonnen-dozen-verzenddozen-exportcontainers/verhuisdozen-archivering/ordnerdoos-geintegreerde-klepsluiting_PDT00427.html"
        'https://www.rajapack.nl/kartonnen-dozen-verzenddozen-exportcontainers/verhuisdozen-archivering_C1070.html,'
        'https://www.rajapack.nl/kartonnen-dozen-verzenddozen-exportcontainers/milieuvriendelijke-postverpakkingen_C1092.html'
    ]

    def parse(self, response):
        links = response.xpath(
            '//div[@class="product__item-grid"]/div[@class="name"]/a/@href'
        ).getall()
        for idx, link in enumerate(links):
            if idx > TestSettings.MAX_ROWS and TESTING:
                break
            yield response.follow(link, callback=self.parse_box_table)

        # follow next page button
        next_page = response.xpath('//a[@class="next"]/@href').get()

        if next_page:
            yield response.follow(next_page.strip(), callback=self.parse)

    def parse_box_table(self, response):
        # iterate over box rows
        boxes_rows = response.xpath('//*[@id="tbody_1"]/tr')
        for idx, row in enumerate(boxes_rows):

            # initialize Item and data object
            box = ScrapingboxesItem()
            table_handler = TableHandlerRajapack(
                header_elements=response.xpath('//thead[@id="thead_1"]/tr/th')
            )

            # crate box data updater
            box_data = ItemUpdater2(item=box, measured_in=table_handler.get_measurement_unit())

            # create data from product description
            box_data.update_item(
                "tags",
                "wall_thickness",  # todo driedubbelgolf wordt niet gepakt, palletdozen
                "description",
                "color",
                'product_type',
                description_element=response.xpath('//*[@test-ihm="ProductName"]')
            )

            # iterate over row indices and update box
            box_data.analyse_table_rows(
                table_handler=table_handler,
                row_elements=row.xpath("./td")
            )

            # create product url
            base_url = response.request.url.split("_")[0]
            product_code = row.xpath('.//*[@class="tooltip-img"]/text()').get()
            try:
                product_url = base_url + "_sku" + product_code + ".html"
                box["url"] = product_url
            except TypeError:
                raise TypeError(base_url, product_code, box)

            # use PriceHandler
            price_handler = PriceHandlerRajapack(item=box,
                                                 # price_multiplier=box['minimum_purchase']
                                                 )

            box["price_table"] = price_handler.create_price_table(
                tier_elements=response.xpath('//*[@id="thead_1"]/tr[2]/th'),
                price_elements=row.xpath('./td[contains(@class, "nobdr")]')
            )

            # HANDLE 'Prijs per doos/pak'
            per_text = response.xpath('//th[contains(@class, "promo")]/b[1]/text()').get()
            multiplier = box.get('minimum_purchase', 1)

            if 'pak' in per_text:
                new_price_table = {}
                for key, value in box['price_table'].items():
                    new_price_table[ key * multiplier ] = round(value / multiplier, 2)
                box['price_table'] = new_price_table
                price_handler.price_table = new_price_table

            box['price_ex_BTW'] = price_handler.get_base_price_from_price_table()

            # add item fields manually
            box["company"] = "Rajapack"
            box["in_stock"] = None
            box['indices_dict'] = table_handler.indices_dict

            yield box
