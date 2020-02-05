import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boxguru.settings')
import django
django.setup()
from products.models import MainCategory, ProductType


box_main_categories = {
    (1, 'vouwdozen'): [(1, 'autolock dozen', 'autolockdozen'), (2, 'deksel dozen', 'dekseldozen'), (3, 'standaard dozen', 'standaarddozen')], #Vouwdozen
    (2, 'verhuis-, ordner- & archiefdozen '): [(4, 'ordner dozen', 'ordnerdozen'), (5, 'verhuis dozen', 'verhuisdozen'), (22, 'archief dozen', 'archiefdozen')],  # Verhuis/order/archiefdozen
    (3, 'palletdozen'): [(6, 'pallet dozen', 'palletdozen')],  # Palletdozen
    (4, 'verzenddozen'): [(7, 'brievenbus dozen', 'brievenbusdozen'), (8, 'envelobox', 'envelobox'), (9, 'post dozen', 'postdozen')],  # Verzenddozen
    (5, 'luxe/geschenk dozen'): [(10, 'geschenk dozen', 'geschenkdozen'), (11, 'giftcard dozen', 'giftcarddozen'), (12, 'gondel dozen', 'gondeldozen'), (13, 'magneet dozen', 'magneetdozen')],  # Speciale dozen
    (6, 'flessendozen'): [(14, 'bier dozen', 'bierdozen'), (15, 'wijn dozen', 'wijndozen')],  # Flessendozen
    (7, 'extra veilige dozen'): [(16, 'UN dozen', 'UN-dozen'), (17, 'fixeer- & zweefverpakkingen', 'fixeer-zweefverpakkingen'), (18, 'schuim dozen', 'schuimdozen')], #Extra veilige dozen
    (8, 'kruiswikkel- & boekverpakkingen'): [(19, 'kruiswikkel- & boekverpakkingen', 'kruiswikkel-boek-verpakkingen')], #Kruiswikkel/boekverpakkingen
    (9, 'schuifdozen'): [(20, 'schuifdozen', 'schuifdozen')], #Overige dozen
    (10,'koeldozen'): [(21, 'koeldozen', 'koeldozen')],  # Koeldozen
}

get_parameter_to_category_product_type_id = {}
for category, product_types in box_main_categories.items():
    for product_type_tuple in product_types:
        get_parameter_to_category_product_type_id[product_type_tuple[2]] = (category[0], product_type_tuple[0])

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