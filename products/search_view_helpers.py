from os.path import join

from django.db.models import Func, Q, When, Case, DecimalField, F
from urllib.parse import unquote
from urllib.parse import urlencode as urlencodeP

from django.db.models.functions import Greatest
from django.utils.http import urlencode
from django.utils.datastructures import MultiValueDict

from products.models import Product

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class Filter:
    def __init__(self, request, current_filter, full_path, filter):

        if type(filter) == tuple or type(filter) == list:
            current_value = str(filter[0])
            self.filter_name = filter[1]
        else:
            current_value = str(filter)
            self.filter_name = filter

        clean_path = full_path.replace('&initial_search=1', '').replace("%2B", '+')
        if current_value in request.GET.getlist(current_filter):
            get_param = '&' + current_filter + '=' + current_value
            self.url = clean_path.replace(get_param, '').replace('+', "%2B")
            self.css_class = 'active'
        else:
            clean_path = clean_path + '&' + current_filter + '=' + current_value
            self.url = clean_path.replace('+', "%2B")
            self.css_class = ''


class Filter2:
    def __init__(self, request, current_filter, filter, remaining_filters):


        # Filter can either be a tuple or list, depending on request.session (somehow): (value, id)
        # Value into string because GET.getlist() returns list of strings
        current_value = str(filter[0])
        self.filter_name = filter[1]

        GET_copy = request.GET.copy()
        # remove initial search parameter
        GET_copy.pop('initial_search', None)

        value_list = GET_copy.getlist(current_filter, None)
        self.checked = False

        if current_value == '':
            GET_copy.setlist(current_filter, [])
            self.css_class = 'deactivate-all'

        elif current_value in value_list:
            value_list.remove(current_value)
            GET_copy.setlist(current_filter, value_list)
            self.css_class = 'active'
            self.checked = True

        else:
            if current_filter in GET_copy:
                GET_copy.update({current_filter: current_value})
            else:
                GET_copy[current_filter] = current_value
            self.css_class = ''

        # Set disabled class
        if (filter[0], current_filter) not in remaining_filters:
            self.css_class += ' disabled'

        # Set page to first page
        GET_copy['page'] = 1

        self.url = request.path + '?' + GET_copy.urlencode() + "#filter"

class FilterVarHeight:
    def __init__(self, request, remaining_filters):
        GET_copy = request.GET.copy()
        # remove initial search parameter
        GET_copy.pop('initial_search', None)

        self.css_class = ''
        self.filter_name = 'Ja, alleen dozen met variabele hoogte'

        if (115, 'product_type') not in remaining_filters:
            self.css_class += 'disabled'
            self.filter_name = 'Ik probeer het toch!'


        if GET_copy.get('variable_height'):
            del GET_copy['variable_height']
            self.css_class += ' active'
            self.filter_name = 'Nee, laat me toch alles zien'

        else:
            GET_copy['variable_height'] = 1

        self.checked = False #todo This need to be removed, is here because of pop-up filters
        GET_copy['page'] = 1
        self.url = request.path + '?' + GET_copy.urlencode() + '#filter'


class FilterVarHeight2:
    def __init__(self, request, filter, remaining_filters):


        # Filter can either be a tuple or list, depending on request.session (somehow): (value, id)
        # Value into string because GET.getlist() returns list of strings
        current_filter = 'product_type'
        current_value = str(filter[0])
        self.filter_name = filter[1]

        GET_copy = request.GET.copy()
        # remove initial search parameter
        GET_copy.pop('initial_search', None)

        value_list = GET_copy.getlist(current_filter, None)
        self.checked = False

        if current_value == '':
            GET_copy.setlist(current_filter, [])
            self.css_class = 'deactivate-all'

        elif current_value in value_list:
            value_list.remove(current_value)
            GET_copy.setlist(current_filter, value_list)
            self.css_class = 'active'
            self.checked = True

        else:
            if current_filter in GET_copy:
                GET_copy.update({current_filter: current_value})
            else:
                GET_copy[current_filter] = current_value
            self.css_class = ''

        # Set disabled class
        if (filter[0], current_filter) not in remaining_filters:
            self.css_class += ' disabled'

        # Set page to first page
        GET_copy['page'] = 1

        self.url = request.path + '?' + GET_copy.urlencode() + "#filter"



class Filter3:
    def __init__(self, request, current_filter, filter):

        if type(filter) == tuple or type(filter) == list:
            # Filter can either be a tuple or list, depending on request.session (somehow): (value, id)
            current_value = str(filter[0])
            self.filter_name = filter[1]
            self.value = current_value
        else:
            # bottles and standard size filters are from value_list, not a queryobject
            current_value = str(filter)
            self.filter_name = filter
            self.value = current_value

        self.filter_query = current_filter

        value_list = request.GET.getlist(current_filter, None)
        self.checked = False
        if current_value == '':
            self.css_class = 'deactivate-all'

        elif current_value in value_list:
            value_list.remove(current_value)
            self.checked = True


def create_filter_list2(filter_class, request, filter_type, filter_list, remaining_filters):
    return [filter_class(request, filter_type, filter, remaining_filters) for filter in filter_list]

def create_filter_list(filter_class, request, filter_type, filter_list):
    return [filter_class(request, filter_type, filter) for filter in filter_list]




# Create round function, arity 1 so rounds to 0 decimals, no input needed
class Round(Func):
    function = 'ROUND'
    arity = 1


# Create absolute function
class Abs(Func):
    function = 'ABS'


def create_sort_order_link(request, order):
    GET_copy = request.GET.copy()
    order = order.replace('-', '')

    if 'sort' not in GET_copy:
        GET_copy['sort'] = order

    if 'by' in GET_copy:
        if GET_copy['by'] == 'ASC':
            GET_copy['by'] = 'DESC'
        else:
            GET_copy['by'] = 'ASC'
    else:
        if GET_copy.get('initial_search') and order == 'max_match':
            GET_copy['by'] = 'DESC'
        else:
            GET_copy['by'] = 'ASC'

    # Set page to first page
    GET_copy['page'] = 1

    full_path = request.path + "?" + GET_copy.urlencode()

    return full_path, GET_copy['by']


def create_sort_headers(request, context):
    # copy GET
    GET_copy = request.GET.copy()

    ordering_swapper = {
        'ASC': 'DESC',
        'DESC': 'ASC'
    }

    # {header: query} dictionary
    header_dict = {
        'category_header': ('product_type', 'DESC'),
        'width_header': ('inner_dim1', 'ASC'),
        'length_header': ('inner_dim2', 'ASC'),
        'height_header': ('inner_dim3', 'ASC'),
        'diameter_header': ('diameter', 'ASC'),
        'match_header': ('max_match', 'ASC'),
        'wall_thickness_header': ('wall_thickness', 'DESC'),
        'color_header': ('color', 'DESC'),
        'standard_size_header': ('standard_size', 'ASC'),
        'bottles_header': ('bottles', 'DESC'),
        'lowest_price_header': ('lowest_price', 'DESC'),
        'price_header': ('price_ex_BTW', 'DESC'),
        'company_header': ('company', 'DESC'),
    }

    for header, query in header_dict.items():
        if request.GET.get('sort') == query[0]:
            GET_copy['by'] = ordering_swapper[request.GET['by']]
            GET_copy['sort'] = query[0]

        else:
            GET_copy['sort'] = query[0]
            GET_copy['by'] = query[1]

        GET_copy['page'] = 1

        context[header] = request.path + '?' + GET_copy.urlencode()

    return context


def create_queryset(request, form, context):
    width = form.cleaned_data.get('width')
    length = form.cleaned_data.get('length')
    height = form.cleaned_data.get('height')
    diameter = form.cleaned_data.get('diameter')
    colors = request.GET.getlist('color')
    wall_thicknesses = request.GET.getlist('wall_thickness')
    main_category = request.GET.get('product_type__main_category')
    standard_size = request.GET.getlist('standard_size')
    bottles = request.GET.getlist('bottles')
    product_types = [product_type for product_type in request.GET.getlist('product_type') if product_type]
    companies = request.GET.getlist('company')
    variable_height_from_get = request.GET.get('variable_height')

    # Deal with variable height
    variable_height = {}
    if '115' in product_types:
        product_types.remove('115')
        variable_height = {'product_type': 115}
        pass
    if variable_height_from_get:
        variable_height =  {'product_type': 115}
    print(variable_height)

    qobjects = []

    # Q objects query
    if colors:
        qcolors = Q(color__in=colors)
        qobjects.append(qcolors)

    if wall_thicknesses:
        qwall_thicknesses = Q(wall_thickness__in=wall_thicknesses)
        qobjects.append(qwall_thicknesses)

    if main_category:
        if main_category == '6':  # (Variable_height)
            variable_height = {'product_type': 115}
        else:
            qmain_category = Q(product_type__main_category=main_category)
            qobjects.append(qmain_category)

    else:
        if context['searched'] == 'box':
            qmain_category = Q(product_type__main_category__in=range(1, 11))
            qobjects.append(qmain_category)
        elif context['searched'] == 'tube':
            qmain_category = Q(product_type__main_category=14)
            qobjects.append(qmain_category)
        elif context['searched'] == 'envelope':
            qmain_category = Q(product_type__main_category=13)
            qobjects.append(qmain_category)

    if len(product_types):
        qproduct_types = Q(product_type__in=product_types)
        qobjects.append(qproduct_types)

    if len(standard_size):
        qstandard_size = Q(standard_size__in=standard_size)
        qobjects.append(qstandard_size)

    if len(bottles):
        qbottles = Q(bottles__in=bottles)
        qobjects.append(qbottles)

    if len(companies):
        qcompanies = Q(company__in=companies)
        qobjects.append(qcompanies)

    # Set error margin for query search range
    error_margin = 50
    error_margin_diameter = 15
    # TODO put error margin in form

    # Set maxmatch variable for template context
    if width or length or height or diameter:
        context['show_match_header'] = True
        max_match = True
    else:
        max_match = False

    if width and not length:
        width = float(width)
        qwidth_length = Q(inner_dim1__range=(width - error_margin, width + error_margin)) | Q(
            inner_dim2__range=(width - error_margin, width + error_margin))
        qobjects.append(qwidth_length)

    elif length and not width:
        length = float(length)
        qwidth_length = Q(inner_dim2__range=(length - error_margin, length + error_margin)) | Q(
            inner_dim1__range=(length - error_margin, length + error_margin))
        qobjects.append(qwidth_length)


    elif width and length:
        width = float(width)
        length = float(length)
        qwidth_length = (Q(inner_dim1__range=(width - error_margin, width + error_margin)) & Q(
            inner_dim2__range=(length - error_margin, length + error_margin))) | (
                                Q(inner_dim2__range=(width - error_margin, width + error_margin)) & Q(
                            inner_dim1__range=(length - error_margin, length + error_margin)))
        qobjects.append(qwidth_length)

    if height:
        height = float(height)
        qheight = Q(inner_dim3__range=(height - error_margin, height + error_margin)) | (
            (Q(inner_variable_dimension_MAX__gte=height) & Q(inner_variable_dimension_MIN__lte=height)))
        qobjects.append(qheight)

    if diameter:
        diameter = float(diameter)
        qdiameter = Q(diameter__range=(diameter - error_margin_diameter, diameter + error_margin_diameter))
        qobjects.append(qdiameter)

    # Create Queryset
    swidth_width_test = Case(
        When(inner_dim1__isnull=False,
             then=(100 - Abs((F('inner_dim1') - width) / F('inner_dim1')) * 100.0)),
        default=0, output_field=DecimalField()
    )
    swidth_length_test = Case(
        When(inner_dim2__isnull=False,
             then=(100 - Abs((F('inner_dim2') - width) / F('inner_dim2')) * 100.0)),
        default=0, output_field=DecimalField()
    )

    slength_width_test = Case(
        When(inner_dim1__isnull=False,
             then=(100 - (Abs(F('inner_dim1') - length) / F('inner_dim1')) * 100.0)),
        default=0, output_field=DecimalField()
    )
    slength_length_test = Case(
        When(inner_dim2__isnull=False,
             then=(100 - (Abs(F('inner_dim2') - length) / F('inner_dim2')) * 100.0)),
        default=0, output_field=DecimalField()
    )

    sheight_height_test = Case(
        When(inner_variable_dimension_MAX__isnull=False,
             then=100),
        When(inner_variable_dimension_MAX__isnull=True,
             then=(100 - (Abs(F('inner_dim3') - height) / F('inner_dim3')) * 100.0)),
        default=0, output_field=DecimalField()
    )

    sdiameter_diameter_test = Case(
        When(diameter__isnull=False,
             then=(100 - (Abs(F('diameter') - diameter) / F('diameter')) * 100.0)),
        default=0, output_field=DecimalField()
    )

    if width and not length and not height:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).order_by().annotate(
            swidth_width_test=swidth_width_test,
            swidth_length_test=swidth_length_test,
            max_match=Round(Greatest('swidth_width_test', 'swidth_length_test'))).distinct()


    elif length and not width and not height and not diameter:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).order_by().annotate(
            slength_width_test=slength_width_test,
            slength_length_test=slength_length_test,
            max_match=Round(Greatest('slength_width_test', 'slength_length_test'))).distinct()

    elif height and not width and not length and not diameter:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).order_by().annotate(
            max_match=Round(sheight_height_test)).distinct()

    elif length and width and not height:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).order_by().annotate(
            slength_width_test=slength_width_test,
            slength_length_test=slength_length_test,
            swidth_width_test=swidth_width_test,
            swidth_length_test=swidth_length_test,
            sww_sll_match=(F('swidth_width_test') + F('slength_length_test')) / 2,
            swl_slw_match=(F('swidth_length_test') + F('slength_width_test')) / 2,
            max_match=Round(Greatest('sww_sll_match', 'swl_slw_match'))).distinct()

    elif length and height and not width:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).order_by().annotate(
            slength_width_test=slength_width_test,
            slength_length_test=slength_length_test,
            sheight_height_test=sheight_height_test,
            wl_match=Greatest('slength_width_test', 'slength_length_test'),
            max_match=Round((F('wl_match') * 2 + F('sheight_height_test')) / 3)).distinct()

    elif width and height and not length:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).order_by().annotate(
            swidth_width_test=swidth_width_test,
            swidth_length_test=swidth_length_test,
            sheight_height_test=sheight_height_test,
            wl_match=Greatest('swidth_width_test', 'swidth_length_test'),
            max_match=Round((F('wl_match') * 2 + F('sheight_height_test')) / 3).distinct()
        )

    elif width and length and height:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).order_by().annotate(
            slength_width_test=slength_width_test,
            slength_length_test=slength_length_test,
            swidth_width_test=swidth_width_test,
            swidth_length_test=swidth_length_test,
            sheight_height_test=sheight_height_test,
            sww_sll_match=(F('swidth_width_test') + F('slength_length_test')) / 2,
            swl_slw_match=(F('swidth_length_test') + F('slength_width_test')) / 2,
            wl_match=Greatest('sww_sll_match', 'swl_slw_match'),
            max_match=Round((F('wl_match') * 2 + F('sheight_height_test')) / 3)).distinct()

    elif diameter and not length:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).order_by().annotate(
            max_match=Round(sdiameter_diameter_test)).distinct()

    elif length and diameter:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).order_by().annotate(
            slength_width_test=slength_width_test,
            slength_length_test=slength_length_test,
            sdiameter_diameter_test=sdiameter_diameter_test,
            slength_match=Greatest('slength_width_test', 'slength_length_test'),
            max_match=Round((F('slength_match') + F('sdiameter_diameter_test')) / 2)).distinct()

    else:
        queryset_qobjects = Product.objects.filter(*qobjects).filter(**variable_height).order_by().distinct()

    return context, queryset_qobjects, max_match


def make_pagination(request, context, queryset):
    page = request.GET.get('page', 1)
    page = int(page)
    paginator = Paginator(queryset, 20)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    if paginator.num_pages > 5:
        index = paginator.page_range.index(products.number)
        if page > 2 and page < paginator.num_pages - 2:
            max_index = len(paginator.page_range)
        else:
            max_index = len(paginator.page_range) - 1

        if page > 4:
            context['broken_start_pagination'] = True
        if page < (paginator.num_pages - 3):
            context['broken_end_pagination'] = True

        start_index = index - 2 if index >= 3 else 1
        end_index = index + 3 if index <= max_index - 3 else max_index
        page_range = paginator.page_range[start_index:end_index]
    else:
        page_range = paginator.page_range[1:len(paginator.page_range) - 1]

    context['products'] = products
    context['page_range'] = page_range
    return context

def order_queryset(request, context, queryset, max_match_possible=False):
    order_by = request.GET.get('sort')
    if order_by:
        # Prepend "-" if order is Ascending
        if request.GET.get('by') == "ASC":
            order_by = "-" + order_by
    else:
        if max_match_possible:
            order_by = '-max_match'
        else:
            order_by = 'price_ex_BTW'

    if 'max_match' in order_by:
        queryset = queryset.order_by(order_by, 'price_ex_BTW')
    elif max_match_possible:
        if 'price_ex_BTW' in order_by:
            queryset = queryset.order_by(order_by, '-max_match')
        else:
            queryset = queryset.order_by(order_by, '-max_match', 'price_ex_BTW')
    else:
        if 'price_ex_BTW' in order_by:
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by(order_by, 'price_ex_BTW')

    context['order_by'] = order_by

    return queryset, context
