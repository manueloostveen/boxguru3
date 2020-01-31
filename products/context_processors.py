from django.db.models import Q
from products.product_categories import box_main_categories as box_cat
from django.http import QueryDict

def footer(request):

    urls = []
    context = {}

    for main_cat_id, categories in box_cat.items():
        for id in categories:
            get_dict = {}
            get_dict['product_type__main_category'] = str(main_cat_id)
            get_dict['product_type'] = str(id[0])
            get_dict['form'] = 'box'

            querydict = QueryDict('', mutable=True)
            querydict.update(**get_dict)
            url = querydict.urlencode()
            urls.append((id[1], url, id[0]))

    context['footer_urls'] = urls

    return context
