import sys
from pathlib import Path

PATH_FILE = Path(__file__).resolve()
PROJECT_DIR = PATH_FILE.parent.parent
sys.path.append(str(PROJECT_DIR))
print(sys.path, 'sys.path')
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boxguru.settings')
import django

django.setup()
from products.models import MainCategory, ProductType

box_main_categories = {
    (4, 'verzenddozen', 'verzenddozen'): [(7, 'brievenbusdozen', 'brievenbusdozen'),
                                          (9, 'postdozen', 'postdozen'), (8, 'envelobox', 'envelobox')],
    (1, 'vouwdozen', 'vouwdozen'): [(3, 'standaard dozen', 'standaarddozen'), (1, 'autolockdozen', 'autolockdozen'), (2, 'dekseldozen', 'dekseldozen'),
                                    ],
    (11, 'verhuisdozen', 'verhuisdozen'): [(5, 'verhuisdozen', 'verhuisdozen')],
    (2, 'archiefdozen', 'archiefdozen'): [(4, 'archiefdozen', 'archiefdozen')],
    (8, 'kruiswikkel- & boekverpakkingen', 'kruiswikkelverpakkingen'): [
        (19, 'kruiswikkel- & boekverpakkingen', 'kruiswikkel-boek-verpakkingen')],

    (3, 'palletdozen', 'palletdozen'): [(6, 'palletdozen', 'palletdozen')],

    (5, 'luxe/geschenk dozen', 'luxe-geschenkdozen'): [(10, 'geschenkdozen', 'geschenkdozen'),
                                                       (11, 'giftcarddozen', 'giftcarddozen'),
                                                       (12, 'gondeldoosjes', 'gondeldoosjes'),
                                                       (13, 'magneetdozen', 'magneetdozen')],
    (6, 'flessendozen', 'flessendozen'): [ (15, 'wijndozen', 'wijndozen'), (14, 'bierdozen', 'bierdozen')],
    (7, 'extra veilige dozen', 'extra-veilige-dozen'): [(16, 'UN-dozen', 'UN-dozen'),
                                                        (17, 'fixeer- & zweefverpakkingen', 'fixeer-zweefverpakkingen'),
                                                        (18, 'schuimdozen', 'schuimdozen')],

    (9, 'schuifdozen', 'schuifdozen'): [(20, 'schuifdozen', 'schuifdozen')],
    (10, 'koeldozen', 'koeldozen'): [(21, 'koeldozen', 'koeldozen')],
}

box_main_categories_clean = {
    'verzenddozen': [(7, 'brievenbusdozen', 'brievenbusdozen'),
                                          (9, 'postdozen', 'postdozen'), (8, 'envelobox', 'envelobox')],
    'vouwdozen': [(3, 'standaard dozen', 'standaarddozen'), (1, 'autolockdozen', 'autolockdozen'), (2, 'dekseldozen', 'dekseldozen'),
                                    ],


    'luxe-geschenkdozen': [(10, 'geschenkdozen', 'geschenkdozen'),
                                                       (11, 'giftcarddozen', 'giftcarddozen'),
                                                       (12, 'gondeldoosjes', 'gondeldoosjes'),
                                                       (13, 'magneetdozen', 'magneetdozen')],
    'flessendozen': [ (15, 'wijndozen', 'wijndozen'), (14, 'bierdozen', 'bierdozen')],
    'extra-veilige-dozen': [(16, 'UN-dozen', 'UN-dozen'),
                                                        (17, 'fixeer- & zweefverpakkingen', 'fixeer-zweefverpakkingen'),
                                                        (18, 'schuimdozen', 'schuimdozen')],

}

box_cat_2_main_cat = {
    1: 1,
    2: 1,
    3: 1,
    4: 2,
    5: 2,
    22: 2,
    6: 3,
    7: 4,
    8: 4,
    9: 4,
    10: 5,
    11: 5,
    12: 5,
    13: 5,
    14: 6,
    15: 6,
    16: 7,
    17: 7,
    18: 7,
    19: 8,
    20: 9,
    21: 10
}

get_parameter_to_category_product_type_id = {}
for category, product_types in box_main_categories.items():
    for product_type_tuple in product_types:
        get_parameter_to_category_product_type_id[product_type_tuple[2]] = (
            category[0], product_type_tuple[0], product_type_tuple[1])

get_parameter_to_main_category_id = {}
for main_cat_tuple in box_main_categories.keys():
    get_parameter_to_main_category_id[main_cat_tuple[2]] = main_cat_tuple[0], main_cat_tuple[1]


def create_main_box_categories():
    for tuple in box_main_categories.keys():
        MainCategory.objects.get_or_create(category_id=tuple[0], category=tuple[1])


def create_product_types():
    for key, values in box_main_categories.items():
        for type in values:
            main_category = MainCategory.objects.get(category_id=key[0])
            ProductType.objects.get_or_create(
                type=type[1],
                product_type_id=type[0],
                main_category=main_category
            )


if __name__ == '__main__':
    create_main_box_categories()
    create_product_types()
