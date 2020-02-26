# -*- coding: utf-8 -*-
import scrapy
from scrapingboxes.items import ScrapingboxesItem
from scrapingboxes.helpers import ItemUpdater, ItemUpdater2, TableHandler, PriceHandler2, all_text_from_elements


class TableHandlerVermeij(TableHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiple_inner_dimensions_words = []
        self.multiple_outer_dimensions_words = []
        self.measurement_words = []
        self.diameter_words = []
        self.standard_size_words = []
        self.bundle_words = ["inhoud"]
        self.outer_dimension_words = []
        self.variable_dimension_words_MIN = []
        self.variable_dimension_words_MAX = []
        self.variable_dimension_words = self.variable_dimension_words_MIN + self.variable_dimension_words_MAX
        self.color_words = ['kleur']
        self.wall_thickness_words = ['kwaliteit']

        # words that can be used to skip certain header names
        self.skip_words = []
        self.create_indices_dict()


class ItemUpdaterVermeij(ItemUpdater2):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        new_wall_thickness_dict = {'duplex': 'solid cardboard',
                                   'container': 'double wall'}  # {'website word': 'single/double/triple wall'}
        self.wall_thickness_dict = {**self.wall_thickness_dict, **new_wall_thickness_dict}

        box_type_codes = {
            "normal box": ['200', '201', '203'],
            "shipping box": ['713', '760', '421', '429', '427', '748', '215', '211'],
            'autolock box': ['711'],
            'cover box': ['309', '320', '330', '306'],
            'binder box': ['444'],
            'cross wrap': ['401', '409'],
            'cover/tray': ['452']
        }

        for type, codes in box_type_codes.items():
            if self.box_type_dict.get(type):
                self.box_type_dict[type] += codes
            else:
                self.box_type_dict[type] = codes


class VermeijtesterSpider(scrapy.Spider):
    name = 'vermeijtester'
    allowed_domains = ['www.vermeij.com']
    start_urls = [
        'https://www.vermeij.com/dozen.html',
        'https://www.vermeij.com/enveloppen.html',
        'https://www.vermeij.com/kokers.html',
        'https://www.vermeij.com/geschenkverpakking.html',
        'https://www.vermeij.com/flesverpakking.html'
    ]
    custom_settings = {'ITEM_PIPELINES': {'scrapingboxes.pipelines.TesterPipeline': 310}}

    def parse(self, response):
        category_links = response.xpath('//*[@class="Shop01catOuterWrapper"]//@href').getall()
        for link in category_links:
            # add see 300 products per page to url
            link += "?page=1&perPage=300"
            yield response.follow(link, self.parse_category)

    def parse_category(self, response):
        product_links = response.xpath('//*[@class="product-table-productname"]//@href').getall()
        for link in product_links:
            yield response.follow(link, self.parse_box)

    def parse_box(self, response):
        box = ScrapingboxesItem()
        # table_handler = TableHandlerTest(header_elements=None)
        box_data = ItemUpdaterVermeij(item=box, measured_in="cm")

        product_description_element = response.xpath(
            '//div[@class="mobile-title-nr"]/h1[@itemprop="name"]/text()')

        box_data.update_item(
            'description', 'all_inner_dimensions', 'tags', 'box_type', 'standard_size',
            text_element=product_description_element
        )


        table_handler = TableHandlerVermeij(
            header_elements=response.xpath('//*[@class="extraspecs-row"]//td[1]')
        )

        box_data.analyse_table_rows(
            row_elements=response.xpath('//*[@class="extraspecs-row"]//tr'),
            table_handler=table_handler
        )

        # create PriceHandler, check if prices are per piece or per box
        box_or_piece_text = response.xpath('//*[@class="Shop01DetailPrijs"]/span[1]/text()').get()
        other_box_or_piece_text = response.xpath('//table[@class="staffelkortingen"]//tr[1]/th[4]').get()

        if box_or_piece_text:
            if 'doos' in box_or_piece_text:
                print('per doos', response.request.url)
                price_handler = PriceHandler2(box, price_multiplier=box['minimum_purchase'])
            elif 'stuk' in box_or_piece_text:
                print('per stuk', response.request.url)
                price_handler = PriceHandler2(box)
            else:
                raise ValueError("No pricehandler, there is something wrong with the box_or_piece_text")


        elif other_box_or_piece_text:
            if 'doos' in other_box_or_piece_text:
                price_handler = PriceHandler2(box, price_multiplier=box['minimum_purchase'])
            elif 'stuk' in other_box_or_piece_text:
                price_handler = PriceHandler2(box)
            else:
                raise ValueError("No pricehandler, there is something wrong with the box_or_piece_text")

        #create price table
        tier_elements = response.xpath('//table[@class="staffelkortingen"]//tr[position() >1]/th')
        if tier_elements:
            price_handler.create_price_table(
                tier_elements=tier_elements,
                price_elements=response.xpath('//table[@class="staffelkortingen"]//tr[position() >1]/td[3]')
            )
            price_handler.get_base_price_from_price_table()

        else:
            price_handler.create_base_price_manually(
                price_element=response.xpath('//*[@class="Shop01DetailPrijs"]/span[2]')
            )

        box['url'] = response.request.url
        box['company'] = 'Vermeij'

        yield box
