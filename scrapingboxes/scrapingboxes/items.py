# -*- coding: utf-8 -*-
import scrapy


class ScrapingboxesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    company = scrapy.Field()
    price_ex_BTW = scrapy.Field()
    minimum_purchase = scrapy.Field()
    in_stock = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    product_type = scrapy.Field()
    inner_dim1 = scrapy.Field()
    inner_dim2 = scrapy.Field()
    inner_dim3 = scrapy.Field()

    height_sorter = scrapy.Field()

    diameter = scrapy.Field()
    inner_variable_dimension_MIN = scrapy.Field()
    inner_variable_dimension_MAX = scrapy.Field()
    outer_variable_dimension_MIN = scrapy.Field()
    outer_variable_dimension_MAX = scrapy.Field()

    variable_height = scrapy.Field()

    outer_dim1 = scrapy.Field()
    outer_dim2 = scrapy.Field()
    outer_dim3 = scrapy.Field()
    standard_size = scrapy.Field()
    color = scrapy.Field()
    wall_thickness = scrapy.Field()
    bottles = scrapy.Field()

    price_table = scrapy.Field()
    all_tags = scrapy.Field()
    extra_dim = scrapy.Field()
    extra_outer_dim = scrapy.Field()
    indices_dict = scrapy.Field()
    test_field = scrapy.Field()
    price_incl_BTW = scrapy.Field()
    lowest_price = scrapy.Field()

    image_urls = scrapy.Field()
    images = scrapy.Field()