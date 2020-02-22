# -*- coding: utf-8 -*-
from django.core.exceptions import MultipleObjectsReturned
from scrapy.exceptions import DropItem
import json
from datetime import datetime
from products.models import Color, ProductType, WallThickness, Product, Tag, TierPrice, Company, MainCategory
from django.forms.models import model_to_dict
from products.product_categories import product_category_dict as pcd
from django.core.files import File


class DjangoTestPipeline(object):
    FLESSEN_DOZEN = 'Flessendozen'
    VEILIGHEIDS_DOZEN = 'Extra veilige dozen'
    SPECIALE_DOZEN = 'Speciale dozen'
    VERZEND_DOZEN = 'Verzenddozen'
    WIKKEL_DOZEN = 'Wikkelverpakkingen en -dozen'
    VERHUIS_DOZEN = 'Verhuis-, ordner- en archiefdozen'
    VARIABELE_DOZEN = 'In hoogte verstelbare dozen'
    VOUWDOZEN = 'Vouwdozen'
    KISTEN = 'Kisten/kratten'
    OVERIGE_DOZEN = 'Overige dozen'
    PALLET_DOZEN = 'Palletdozen'

    ENVELOPPEN = 'Enveloppen & zakken'
    OVERIG = 'Overig'
    VERZENDKOKERS = 'Verzendkokers'

    category_dict = {
        'UN dozen': pcd['VEILIGHEIDS_DOZEN'],
        'geschenk dozen': pcd['SPECIALE_DOZEN'],
        "wijn dozen": pcd['FLESSEN_DOZEN'],
        "bier dozen": pcd['FLESSEN_DOZEN'],
        'enveloppen van karton': pcd['ENVELOPPEN'],
        'luchtkussen enveloppen': pcd['ENVELOPPEN'],
        'waterafstotende enveloppen': pcd['ENVELOPPEN'],
        'paklijst enveloppen': pcd['ENVELOPPEN'],
        'schuim enveloppen': pcd['ENVELOPPEN'],
        'standaard enveloppen': pcd['ENVELOPPEN'],
        'envelobox': pcd['VERZEND_DOZEN'],
        'magneet dozen': pcd['SPECIALE_DOZEN'],
        'verzend zakken': pcd['ENVELOPPEN'],
        'trapezium kokers': pcd['VERZENDKOKERS'],
        'driekhoeks kokers': pcd['VERZENDKOKERS'],
        'vierkante kokers': pcd['VERZENDKOKERS'],
        "ronde kokers": pcd['VERZENDKOKERS'],
        "dozen inserts": pcd['OVERIG'],
        "flessen dozen": pcd['FLESSEN_DOZEN'],
        "verzend dozen": pcd['VERZEND_DOZEN'],
        "kruiswikkel/boek verpakkingen": pcd['WIKKEL_DOZEN'],
        "verhuis dozen": pcd['VERHUIS_DOZEN'],
        'variabele hoogte dozen': pcd['VARIABELE_DOZEN'],
        "autolock dozen": pcd['VOUWDOZEN'],
        "deksel dozen": pcd['VOUWDOZEN'],
        "archief dozen": pcd['VERHUIS_DOZEN'],
        "brievenbus dozen": pcd['VERZEND_DOZEN'],
        "kisten/bakken": pcd['KISTEN'],
        "schuim dozen": pcd['VEILIGHEIDS_DOZEN'],
        "fixeer-/zweef verpakkingen": pcd['VEILIGHEIDS_DOZEN'],
        "ordner dozen": pcd['VERHUIS_DOZEN'],
        "boek verpakkingen": pcd['WIKKEL_DOZEN'],
        "koeldozen": pcd['SPECIALE_DOZEN'],
        "feestelijke dozen": pcd['SPECIALE_DOZEN'],
        "stans dozen": pcd['OVERIGE_DOZEN'],
        'gondel dozen': pcd['SPECIALE_DOZEN'],
        'giftcard dozen': pcd['SPECIALE_DOZEN'],
        'schuifdozen': pcd['OVERIGE_DOZEN'],
        'magazijn doos': pcd['OVERIGE_DOZEN'],
        'kartonnen platen': pcd['OVERIG'],
        "pallet dozen": pcd['PALLET_DOZEN'],
        'standaard dozen': pcd['VOUWDOZEN'],
        'paraat dozen': pcd['OVERIGE_DOZEN'],
        'opvulmateriaal': pcd['OVERIG']
    }

    def open_spider(self, spider):
        if spider.name == 'viv':
            # Company.objects.get(company='Verpakkingsindustrie Veenendaal').delete()
            Product.objects.filter(company__company='Verpakkingsindustrie Veenendaal').delete()
        elif spider.name == 'vvs':
            Product.objects.filter(company__company='Verzendverpakkingenshop.nl').delete()
        elif spider.name == 'rajapack':
            Product.objects.filter(company__company='Rajapack').delete()
        elif spider.name == 'dozen':
            Product.objects.filter(company__company='Dozen.nl').delete()
        elif spider.name == 'kartonnendozen123':
            Product.objects.filter(company__company='123Kartonnendozen.nl').delete()
        elif spider.name == 'paardekooper':
            Product.objects.filter(company__company='Paardekooper').delete()
        elif spider.name == 'pacoverpakkingen':
            Product.objects.filter(company__company='PacoVerpakkingen').delete()
        elif spider.name == 'tarra':
            Product.objects.filter(company__company='Tarra-pack').delete()
        elif spider.name == 'tupak':
            Product.objects.filter(company__company='Tupak').delete()
        elif spider.name == 'europresto':
            Product.objects.filter(company__company='Europresto').delete()
        elif spider.name == 'vermeij':
            Product.objects.filter(company__company='Vermeij').delete()

    def process_item(self, item, spider):

        company, _ = Company.objects.get_or_create(company=item.get('company'))
        color, _ = Color.objects.get_or_create(color=item.get('color'))
        #Todo ProductType needs not null product_type_id
        product_type, pt_created = ProductType.objects.get_or_create(type=item.get('product_type'))
        wall_thickness, _ = WallThickness.objects.get_or_create(wall_thickness=item.get('wall_thickness'))

        tags = []
        for item_tag in item.get('all_tags'):
            tag, _ = Tag.objects.get_or_create(tag=item_tag)
            tags.append(tag)

        tier_prices = []
        for tier, price in item.get('price_table').items():
            try:
                tier_price, _ = TierPrice.objects.get_or_create(tier=tier, price=price)
            except TierPrice.MultipleObjectsReturned:
                tier_price = TierPrice.objects.filter(tier=tier, price=price).order_by('id').first()
            tier_prices.append(tier_price)

        excludable_keys = ['all_tags', 'indices_dict', 'test_field', 'price_table', 'color', 'wall_thickness',
                           'product_type', 'company', 'images', 'image_urls']
        product_dict = {key: value for key, value in item.items() if key not in excludable_keys}

        # Calculate volume of box
        if item.get('inner_variable_dimension_MAX') and item.get('inner_dim1') and item.get('inner_dim2'):
            volume = round((item['inner_variable_dimension_MAX'] * item['inner_dim1'] * item['inner_dim2']) / 1000000.0,
                           4)
        elif item.get('inner_dim3') and item.get('inner_dim1') and item.get('inner_dim2'):
            volume = round((item['inner_dim3'] * item['inner_dim1'] * item['inner_dim2']) / 1000000.0, 4)
        else:
            volume = 0.0000

        new_product, product_created = Product.objects.get_or_create(
            **product_dict,
            volume=volume,
            color=color,
            wall_thickness=wall_thickness,
            company=company,
            product_type=product_type,
        )

        # Add tags and price table
        new_product.tags.clear()
        new_product.tags.add(*tags)
        new_product.price_table.clear()
        new_product.price_table.add(*tier_prices)

        # add image to product
        if len(item['images']):
            new_product.product_image = item['images'][0]['path']
            new_product.save()

        return item


class TesterPipeline(object):

    def open_spider(self, spider):
        filename_results = "./testresults/" + spider.name + datetime.now().strftime("%Y%m%d-%H%M%S") + ".jl"
        self.results_file = open(filename_results, 'w')
        self.total_results = []
        self.total_urls = []

    def close_spider(self, spider):
        counter = 1

        for result in self.total_results:
            line = str(counter) + " " + json.dumps(result) + "\n"
            self.results_file.write(line)
            counter += 1

        counter = 1

        for url in self.total_urls:
            line = str(counter) + " " + json.dumps(url) + "\n"
            self.results_file.write(line)
            counter += 1

        self.results_file.close()

    def process_item(self, item, spider):
        # gather item tags for analysing purposes
        test_result = item.get('test_field')
        if isinstance(test_result, list):
            for result in test_result:
                if result not in self.total_results:
                    self.total_results.append(result)
                    self.total_urls.append(item.get('url'))
        else:
            if test_result not in self.total_results:
                self.total_results.append(test_result)
                self.total_urls.append(item.get('url'))

        return item


class ScrapingboxesPipeline(object):

    def open_spider(self, spider):
        filename_tags = "./tags/" + spider.name + datetime.now().strftime("%Y%m%d-%H%M%S") + ".jl"
        self.tag_file = open(filename_tags, 'w')

        filename_dropped_items = "./results/" + spider.name + "DroppedItems" + datetime.now().strftime(
            "%Y%m%d-%H%M%S") + ".jl"
        self.dropped_items_file = open(filename_dropped_items, 'w', encoding='utf-8', newline="\n")

        self.total_of_tags = []
        self.dropped_items = 0

    def close_spider(self, spider):
        for tag in self.total_of_tags:
            line = json.dumps(tag) + "\n"
            self.tag_file.write(line)

        print('Dropped Items: ', self.dropped_items)

        self.dropped_items_file.write(f"Dropped Items: {self.dropped_items}")
        self.tag_file.close()

    inner_dimensions = [
        "inner_dim1",
        "inner_dim2",
        "inner_dim3",
    ]

    outer_dimensions = [
        "outer_dim1",
        "outer_dim2",
        "outer_dim3",
    ]

    inner_variable_dimensions = [
        "inner_variable_dimension_MIN",
        "inner_variable_dimension_MAX",
    ]

    outer_variable_dimensions = [
        "outer_variable_dimension_MIN",
        "outer_variable_dimension_MAX",
    ]

    def drop_item(self, item, error, error_count=None):
        if error == "DimensionError":
            drop_string = f"Dimension error in item: \n inner_dims: {self.inner_dims} \n inner_variable_dims: {self.inner_variable_dims} \n url: {item.get('url')}"

        drop_item = DropItem(drop_string)
        self.dropped_items += 1

        self.dropped_items_file.write("--- DROPPED ITEM ---\n")

        json.dump(dict(item), self.dropped_items_file, ensure_ascii=False, indent=4)

        error_strings = [
            f"Dimension error in item:",
            f"inner_dims: {self.inner_dims}",
            f"inner_variable_dims: {self.inner_variable_dims}",
            f'error_number: {error_count}'
        ]

        for string in error_strings:
            self.dropped_items_file.write("\n")
            self.dropped_items_file.write(
                json.dumps(string, indent=2))
        self.dropped_items_file.write("\n________________________________________________________________\n\n")

        raise drop_item

    def check_box_dimensions(self, item):

        self.inner_dims = []
        self.outer_dims = []
        self.inner_variable_dims = []
        self.outer_variable_dims = []

        # check all dimensions of item
        for inner_dim in self.inner_dimensions:
            if inner_dim in item:
                self.inner_dims.append(f"{inner_dim}: {item[inner_dim]}")
        for outer_dim in self.outer_dimensions:
            if outer_dim in item:
                self.outer_dims.append(f"{outer_dim}: {item[outer_dim]}")
        for inner_var_dim in self.inner_variable_dimensions:
            if inner_var_dim in item:
                self.inner_variable_dims.append(f"{inner_var_dim}: {item[inner_var_dim]}")
        for outer_var_dim in self.outer_variable_dimensions:
            if outer_var_dim in item:
                self.outer_variable_dims.append(f"{outer_var_dim}: {item[outer_var_dim]}")

        # Gets rid of wrong measured products (Paarekooper)
        if item.get('inner_dim1'):
            if item['inner_dim1'] > 2000:
                raise self.drop_item(item, error="DimensionError", error_count=-1)

        if item['product_type'] in ["wijn dozen", "bier dozen", "flessen dozen"]:
            if item.get('extra_dim'):
                item['bottles'] = item['extra_dim']
            elif len(self.inner_dims) == 1:
                item['bottles'] = item.pop('inner_dim1')

        # Set variable height
        if len(self.inner_variable_dims):
            item['variable_height'] = True

        else:
            item['variable_height'] = False

        # Set height sorter value
        if item.get('inner_variable_dimension_MAX'):
            item['height_sorter'] = item['inner_variable_dimension_MAX']
        elif item.get('inner_dim3'):
            item['height_sorter'] = item['inner_dim3']

        # add 0 if product only has MAX variable height
        if len(self.inner_variable_dims) == 1:
            if item.get('inner_variable_dimension_MAX') and not item.get('inner_variable_dimension_MIN'):
                item['inner_variable_dimension_MIN'] = 0


        elif not len(self.inner_dims):
            if item.get('product_type') in ["wijn dozen", "bier dozen", "flessen dozen"] and item.get('bottles'):
                pass

        if len(self.inner_dims) == 3:
            pass
        #     if not self.inner_variable_dims:
        #         if not item.get('product_type'):
        #             raise self.drop_item(item, error="DimensionError", error_count=0)
        #
        #     else:
        #         self.drop_item(item, error="DimensionError", error_count=1)

        elif len(self.inner_dims) == 2:
            tolerable_2dim_products = ['verzend zakken', 'kartonnen platen', 'boek verpakkingen', 'dozen inserts']

            if len(self.inner_variable_dims):
                pass

            elif "koker" in item.get("product_type"):
                if len(self.inner_variable_dims) == 0:
                    if item['inner_dim1'] < item['inner_dim2']:
                        item['diameter'] = item.pop('inner_dim1')
                    else:
                        item['diameter'] = item.pop('inner_dim2')

            elif item.get('product_type') in tolerable_2dim_products:
                pass

            elif 'envelop' in item.get('product_type'):
                pass

            elif item['product_type'] == 'brievenbus dozen':
                if item.get('extra_dim'):
                    item['inner_dim3'] = item.pop('extra_dim')


            #
            # elif len(self.inner_variable_dims) == 1:
            #     pass

            else:
                self.drop_item(item, error="DimensionError", error_count=3)


        elif len(self.inner_dims) == 1:

            if 'koker' in item['product_type'] and not item.get('diameter'):
                item['diameter'] = item.pop('inner_dim1')
            elif item['product_type'] == 'kartonnen platen':
                pass
            else:
                self.drop_item(item, error="DimensionError", error_count=4)

        elif len(self.inner_dims) == 0 and len(self.outer_dims) == 3:
            item["inner_dim1"] = item.pop("outer_dim1")
            item["inner_dim2"] = item.pop("outer_dim2")
            item["inner_dim3"] = item.pop("outer_dim3")

        else:
            self.drop_item(item, error="DimensionError", error_count=5)

        if not item.get('product_type'):
            self.drop_item(item, error="DimensionError", error_count=6)

    def process_item(self, item, spider):
        # check if not too much dimensions, box cannot be variable AND normal
        # check if price

        # check if product has product type
        if not item.get('product_type'):
            self.drop_item(item, error='None')

        # gather item tags for analysing purposes
        for tag in item.get('all_tags'):
            if tag not in self.total_of_tags:
                self.total_of_tags.append(tag)

        # if product has no wall thickness, wall thickness is set to single wall
        if not item.get('wall_thickness'):
            item['wall_thickness'] = 'standaard'
            # todo What to do with envelopes and bags?

        # create lowest price
        lowest_price = item['price_ex_BTW']
        if item.get('price_table'):
            for price in item['price_table'].values():
                if isinstance(price, float):
                    if price < lowest_price:
                        lowest_price = price
        item['lowest_price'] = lowest_price

        # check all dimensions of item
        self.check_box_dimensions(item)

        # adjust shipping box to mailbox box
        if item.get('inner_dim3') and item.get('inner_dim2'):
            if item.get('inner_dim3') <= 28.0 and item.get('product_type') == 'post dozen':
                if item.get('inner_dim2') <= 250 or item.get('inner_dim3') <= 250:
                    item['product_type'] = 'brievenbus dozen'
                    # todo: check other dimensions as well!

        # create price incl btw
        item['price_incl_BTW'] = round(item['price_ex_BTW'] * 1.21, 2)

        # set color to unknown if no color found by scraper
        if not item.get('color'):
            item['color'] = 'standaard'

        return item
