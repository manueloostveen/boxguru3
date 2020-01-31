import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boxguru.settings')
import django
django.setup()
from products.models import MainCategory, ProductType


box_main_categories = {
    (1, 'vouwdozen'): [(1, 'autolock dozen'), (2, 'deksel dozen'), (3, 'standaard dozen')], #Vouwdozen
    (2, 'verhuis-, ordner- & archiefdozen '): [(4, 'ordner dozen'), (5, 'verhuis dozen'), (22, 'archief dozen')],  # Verhuis/order/archiefdozen
    (3, 'palletdozen'): [(6, 'pallet dozen')],  # Palletdozen
    (4, 'verzenddozen'): [(7, 'brievenbus dozen'), (8, 'envelobox'), (9, 'post dozen')],  # Verzenddozen
    (5, 'luxe/geschenk dozen'): [(10, 'geschenk dozen'), (11, 'giftcard dozen'), (12, 'gondel dozen'), (13, 'magneet dozen')],  # Speciale dozen
    (6, 'flessendozen'): [(14, 'bier dozen'), (15, 'wijn dozen')],  # Flessendozen
    (7, 'extra veilige dozen'): [(16, 'UN dozen'), (17, 'fixeer-/zweef verpakkingen'), (18, 'schuim dozen')], #Extra veilige dozen
    (8, 'kruiswikkel-/boekverpakkingen'): [(19, 'kruiswikkel/boek verpakkingen')], #Kruiswikkel/boekverpakkingen
    (9, 'schuifdozen'): [(20, 'schuifdozen')], #Overige dozen
    (10,'koeldozen'): [(21, 'koeldozen')],  # Koeldozen
}

def create_main_box_categories():
    for tuple in box_main_categories.keys():
        MainCategory.objects.get_or_create(category_id=tuple[0], category=tuple[1])

def create_product_types():
    for key, values in box_main_categories.items():
        for type in values:
            main_category = MainCategory.objects.get(category_id=key[0])
            ProductType.objects.create(
                type=type[1],
                product_type_id=type[0],
                main_category=main_category
            )


if __name__ == '__main__':
    create_main_box_categories()
    create_product_types()