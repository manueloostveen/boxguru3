from os.path import join

from django.db.models import Func, Q, When, Case, DecimalField, F
from urllib.parse import unquote
from urllib.parse import urlencode as urlencodeP

from django.db.models.functions import Greatest
from django.utils.http import urlencode
from django.utils.datastructures import MultiValueDict

from products.models import Product


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
    def __init__(self, request, current_filter, filter):

        if type(filter) == tuple or type(filter) == list:
            # Filter can either be a tuple or list, depending on request.session (somehow): (value, id)
            current_value = str(filter[0])
            self.filter_name = filter[1]
        else:
            # bottles and standard size filters are from value_list, not a queryobject
            current_value = str(filter)
            self.filter_name = filter

        GET_copy = request.GET.copy()
        GET_copy.pop('initial_search', None)
        value_list = GET_copy.getlist(current_filter, None)

        if current_value == '':
            GET_copy.setlist(current_filter, [])
            self.css_class = 'deactivate-all'

        elif current_value in value_list:
            value_list.remove(current_value)
            GET_copy.setlist(current_filter, value_list)
            self.css_class = 'active'

        else:
            if current_filter in GET_copy:
                GET_copy.update({current_filter: current_value})
            else:
                GET_copy[current_filter] = current_value
            self.css_class = ''

        self.url = request.path + '?' + GET_copy.urlencode()



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
        'category_header': 'product_type',
        'width_header': 'inner_dim1',
        'length_header': 'inner_dim2',
        'height_header': 'inner_dim3',
        'diameter_header': 'diameter',
        'match_header': 'max_match',
        'wall_thickness_header': 'wall_thickness',
        'color_header': 'color',
        'standard_size_header': 'standard_size',
        'bottles_header': 'bottles',
        'lowest_price_header': 'lowest_price',
        'price_header': 'price_ex_BTW',
        'company_header': 'company',
    }

    for header, query in header_dict.items():
        if request.GET.get('sort') == query:
            GET_copy['by'] = ordering_swapper[request.GET['by']]
            GET_copy['sort'] = query

        else:
            GET_copy['sort'] = query
            GET_copy['by'] = 'ASC'

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

    # Deal with variable height
    variable_height = {}
    if '115' in product_types:
        product_types.remove('115')
        variable_height = {'product_type': 115}


    qobjects = []

    # Q objects query
    if colors:
        qcolors = Q(color__in=colors)
        qobjects.append(qcolors)

    if wall_thicknesses:
        qwall_thicknesses = Q(wall_thickness__in=wall_thicknesses)
        qobjects.append(qwall_thicknesses)

    if main_category:
        if main_category == '6': #(Variable_height)
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
    if width and not length and not height:
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
        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).distinct().annotate(
            swidth_width_test=swidth_width_test).annotate(
            swidth_length_test=swidth_length_test).annotate(
            max_match=Round(Greatest('swidth_width_test', 'swidth_length_test')))


    elif length and not width and not height and not diameter:

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

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).distinct().annotate(
            slength_width_test=slength_width_test).annotate(
            slength_length_test=slength_length_test).annotate(
            max_match=Round(Greatest('slength_width_test', 'slength_length_test')))

    elif height and not width and not length and not diameter:

        sheight_height_test = Case(
            When(inner_variable_dimension_MAX__isnull=False,
                 then=100),
            When(inner_variable_dimension_MAX__isnull=True,
                 then=(100 - (Abs(F('inner_dim3') - height) / F('inner_dim3')) * 100.0)),
            default=0, output_field=DecimalField()
        )

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).distinct().annotate(
            max_match=Round(sheight_height_test))

    elif length and width and not height:

        swidth_width_test = Case(
            When(inner_dim1__isnull=False,
                 then=(100 - (Abs(F('inner_dim1') - width) / F('inner_dim1')) * 100.0)),
            default=0, output_field=DecimalField()
        )
        swidth_length_test = Case(
            When(inner_dim2__isnull=False,
                 then=(100 - (Abs(F('inner_dim2') - width) / F('inner_dim2')) * 100.0)),
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

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).distinct().annotate(
            slength_width_test=slength_width_test).annotate(
            slength_length_test=slength_length_test).annotate(
            swidth_width_test=swidth_width_test).annotate(
            swidth_length_test=swidth_length_test).annotate(
            sww_sll_match=(F('swidth_width_test') + F('slength_length_test')) / 2).annotate(
            swl_slw_match=(F('swidth_length_test') + F('slength_width_test')) / 2).annotate(
            max_match=Round(Greatest('sww_sll_match', 'swl_slw_match')))


    elif width and length and height:

        swidth_width_test = Case(
            When(inner_dim1__isnull=False,
                 then=(100 - (Abs(F('inner_dim1') - width) / F('inner_dim1')) * 100.0)),
            default=0, output_field=DecimalField()
        )
        swidth_length_test = Case(
            When(inner_dim2__isnull=False,
                 then=(100 - (Abs(F('inner_dim2') - width) / F('inner_dim2')) * 100.0)),
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
                 then=(100 - (Abs(F('inner_dim3') - length) / F('inner_dim3')) * 100.0)),
            default=0, output_field=DecimalField()
        )

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).distinct().annotate(
            slength_width_test=slength_width_test).annotate(
            slength_length_test=slength_length_test).annotate(
            swidth_width_test=swidth_width_test).annotate(
            swidth_length_test=swidth_length_test).annotate(
            sheight_height_test=sheight_height_test).annotate(
            sww_sll_match=(F('swidth_width_test') + F('slength_length_test')) / 2).annotate(
            swl_slw_match=(F('swidth_length_test') + F('slength_width_test')) / 2).annotate(
            wl_match=Greatest('sww_sll_match', 'swl_slw_match')).annotate(
            max_match=Round((F('wl_match') * 2 + F('sheight_height_test')) / 3))

    elif diameter and not length:
        sdiameter_diameter_test = Case(
            When(diameter__isnull=False,
                 then=(100 - (Abs(F('diameter') - diameter) / F('diameter')) * 100.0)),
            default=0, output_field=DecimalField()
        )
        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).distinct().annotate(
            max_match=Round(sdiameter_diameter_test))

    elif length and diameter:
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

        sdiameter_diameter_test = Case(
            When(diameter__isnull=False,
                 then=(100 - (Abs(F('diameter') - diameter) / F('diameter')) * 100.0)),
            default=0, output_field=DecimalField()
        )

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).filter(**variable_height).distinct().annotate(
            slength_width_test=slength_width_test).annotate(
            slength_length_test=slength_length_test).annotate(
            sdiameter_diameter_test=sdiameter_diameter_test).annotate(
            slength_match=Greatest('slength_width_test', 'slength_length_test')).annotate(
            max_match=Round((F('slength_match') + F('sdiameter_diameter_test')) / 2))


    else:
        queryset_qobjects = Product.objects.filter(*qobjects).filter(**variable_height).distinct()

    print(variable_height, '**variable_height')
    print(qobjects, 'qobjects')
    return context, queryset_qobjects, max_match
