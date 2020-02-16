from django.db.models import Q
from products.populate_db import box_main_categories
from django.http import QueryDict

def footer(request):

    urls = []
    context = {}

    # for main_category, product_types in box_main_categories.items():
    #     for product_type in product_types:
    #         get_dict = {}
    #         # get_dict['product_type__main_category'] = str(main_category[0])
    #         # get_dict['product_type__product_type_id'] = str(product_type[0])
    #         # get_dict['form'] = 'box'
    #
    #         querydict = QueryDict('', mutable=True)
    #         querydict.update(**get_dict)
    #         url = querydict.urlencode()
    #         urls.append((product_type[1], url, product_type[2]))
    #
    # context['footer_urls'] = urls
    context['footer_all_categories'] = box_main_categories

    return context
