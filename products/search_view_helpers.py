from collections import defaultdict
from django.db.models import Func, Q, When, Case, DecimalField, F, IntegerField, Min, FloatField, Max, Count
from django.db.models.functions import Greatest
from django.utils.http import urlencode
from products.models import Product, ProductType, Color, Company, WallThickness
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from products.product_fit_logic import RectangularProduct, CylindricalProduct
import json


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
    def __init__(self, request, current_filter, filter, remaining_filters, count_dict):

        # Value into string because GET.getlist() returns list of strings
        current_value = str(filter[0])
        self.filter_name = filter[1]

        # Get filter count from count dict, pass '', this is the clear all filter
        if not current_value == '':
            try:
                if current_filter == 'product_type_id':
                    current_filter = 'product_type__product_type_id'
                self.count = '(' + str(count_dict[current_filter][filter[0]]) + ')'
            except KeyError:
                self.count = ''

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


class FilterLikedBoxes:

    def __init__(self, request):
        GET_copy = request.GET.copy()
        liked = GET_copy.pop('liked', None)
        GET_copy.pop('initial_search', None)

        if liked:
            self.url = request.path + '?' + GET_copy.urlencode() + "#table"
            self.css_class = 'active'
            self.text = 'TOON ALLE ZOEKRESULTATEN'
            self.text_alt = self.text

        else:
            GET_copy['liked'] = 1
            self.url = request.path + '?' + GET_copy.urlencode() + "#table"
            self.css_class = ''
            self.text = 'MIJN BEWAARDE DOZEN'
            self.text_alt = 'ALLEEN MIJN BEWAARDE DOZEN'


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

        self.checked = False  # todo This need to be removed, is here because of pop-up filters
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


def create_filter_list2(filter_class, request, filter_type, filter_list, remaining_filters, count_dict):
    return [filter_class(request, filter_type, filter, remaining_filters, count_dict) for filter in filter_list]


def create_filter_list(filter_class, request, filter_type, filter_list):
    return [filter_class(request, filter_type, filter) for filter in filter_list]


# Create round function, arity 1 so rounds to 0 decimals, no input needed
class Round(Func):
    function = 'ROUND'
    arity = 1


# Create absolute function
class Abs(Func):
    function = 'ABS'


def create_sort_order_link(request):
    GET_copy = request.GET.copy()
    show_sort_order = True

    if 'by' in GET_copy:
        if GET_copy['by'] == 'ASC':
            GET_copy['by'] = 'DESC'
        else:
            GET_copy['by'] = 'ASC'
    else:
        show_sort_order = False

    # Set page to first page
    GET_copy['page'] = 1

    full_path = request.path + "?" + GET_copy.urlencode() + "#table"

    return full_path, show_sort_order


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
        'height_header': ('height_sorter', 'ASC'),
        'diameter_header': ('diameter', 'ASC'),
        'match_header': ('max_match', 'ASC'),
        'wall_thickness_header': ('wall_thickness', 'DESC'),
        'color_header': ('color', 'DESC'),
        'standard_size_header': ('standard_size', 'ASC'),
        'bottles_header': ('bottles', 'DESC'),
        'lowest_price_header': ('lowest_price', 'DESC'),
        'price_header': ('price_ex_BTW', 'DESC'),
        'company_header': ('company', 'DESC'),
        'volume_header': ('volume', 'DESC')
    }

    current_sort_dict = {
        'product_type': 'Type doos',
        'inner_dim1': 'Breedte',
        'inner_dim2': 'Lengte',
        'height_sorter': 'Hoogte',
        'max_match': 'Zoekmatch',
        'price_ex_BTW': 'Prijs',
        'lowest_price': 'Laagste bulkprijs'
    }

    context['sort_order_link'], context['show_sort_order_link'] = create_sort_order_link(request)
    context['current_sort'] = current_sort_dict.get(request.GET.get('sort'))
    context['sort'] = request.GET.get('by')

    for header, query in header_dict.items():
        if request.GET.get('sort') == query[0]:
            GET_copy['by'] = ordering_swapper[request.GET['by']]
            GET_copy['sort'] = query[0]

        else:
            GET_copy['sort'] = query[0]
            GET_copy['by'] = query[1]

        GET_copy['page'] = 1

        context[header] = request.path + '?' + GET_copy.urlencode() + "#table"

    return context


def create_queryset(request, form, context, initial_product_type=None):
    width = form.cleaned_data.get('width')
    length = form.cleaned_data.get('length')
    height = form.cleaned_data.get('height')
    diameter = form.cleaned_data.get('diameter')
    colors = request.GET.getlist('color')
    wall_thicknesses = request.GET.getlist('wall_thickness')
    main_category = form.cleaned_data.get('category')
    standard_size = request.GET.getlist('standard_size')
    bottles = request.GET.getlist('bottles')
    companies = request.GET.getlist('company')
    variable_height = form.cleaned_data.get('variable_height')

    if initial_product_type:
        product_types = [initial_product_type]
    else:
        product_types = [product_type for product_type in request.GET.getlist('product_type__product_type_id') if
                         product_type]

    qobjects = []

    # Show liked boxes
    only_liked_boxes = request.GET.get('liked')

    context['saved_boxes'] = json.loads(request.COOKIES.get('saved_boxes'))

    if only_liked_boxes:
        if only_liked_boxes == '2':
            no_saved_boxes_message = '<h4>Je hebt nog geen dozen bewaard om te vergelijken!</h4><p> Doe hierboven een zoekopdracht en bewaar dozen met de "bewaarknop".</p>'
        else:
            no_saved_boxes_message = '<h4>Je hebt nog geen dozen bewaard om te vergelijken!</h4><p> Bewaar dozen in de zoekresultaten met de "bewaarknop".</p>'
        saved_boxes = request.COOKIES.get('saved_boxes')
        if saved_boxes:
            saved_boxes = json.loads(saved_boxes)
            qsaved = Q(pk__in=saved_boxes)
            if not len(saved_boxes):
                context['saved_boxes_message'] = no_saved_boxes_message
        else:
            context['saved_boxes_message'] = no_saved_boxes_message
            qsaved = Q(pk__in=[])

        qobjects.append(qsaved)

    # Deal with variable height
    qvariable_height = Q()
    if variable_height == '1':
        qvariable_height = Q(variable_height=True)
    elif variable_height == '2':
        qvariable_height = Q(variable_height=False)

    qobjects.append(qvariable_height)

    # Q objects query
    if colors:
        qcolors = Q(color__in=colors)
        qobjects.append(qcolors)

    if wall_thicknesses:
        qwall_thicknesses = Q(wall_thickness__in=wall_thicknesses)
        qobjects.append(qwall_thicknesses)

    if main_category:
        qmain_category = Q(product_type__main_category=main_category)
        qobjects.append(qmain_category)

    else:
        if context['searched'] == 'box':
            qmain_category = Q(product_type__main_category__category_id__in=list(range(1, 11)))
            qobjects.append(qmain_category)
        # elif context['searched'] == 'tube':
        #     qmain_category = Q(product_type__main_category=14)
        #     qobjects.append(qmain_category)
        # elif context['searched'] == 'envelope':
        #     qmain_category = Q(product_type__main_category=13)
        #     qobjects.append(qmain_category)

    if len(product_types):
        qproduct_types = Q(product_type__product_type_id__in=product_types)
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
        ).order_by().annotate(
            swidth_width_test=swidth_width_test,
            swidth_length_test=swidth_length_test,
            max_match=Round(Greatest('swidth_width_test', 'swidth_length_test'))).distinct()


    elif length and not width and not height and not diameter:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).order_by().annotate(
            slength_width_test=slength_width_test,
            slength_length_test=slength_length_test,
            max_match=Round(Greatest('slength_width_test', 'slength_length_test'))).distinct()

    elif height and not width and not length and not diameter:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).order_by().annotate(
            max_match=Round(sheight_height_test)).distinct()

    elif length and width and not height:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).order_by().annotate(
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
        ).order_by().annotate(
            slength_width_test=slength_width_test,
            slength_length_test=slength_length_test,
            sheight_height_test=sheight_height_test,
            wl_match=Greatest('slength_width_test', 'slength_length_test'),
            max_match=Round((F('wl_match') * 2 + F('sheight_height_test')) / 3)).distinct()

    elif width and height and not length:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).order_by().annotate(
            swidth_width_test=swidth_width_test,
            swidth_length_test=swidth_length_test,
            sheight_height_test=sheight_height_test,
            wl_match=Greatest('swidth_width_test', 'swidth_length_test'),
            max_match=Round((F('wl_match') * 2 + F('sheight_height_test')) / 3)).distinct()


    elif width and length and height:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).order_by().annotate(
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
        ).order_by().annotate(
            max_match=Round(sdiameter_diameter_test)).distinct()

    elif length and diameter:

        queryset_qobjects = Product.objects.filter(
            *qobjects
        ).order_by().annotate(
            slength_width_test=slength_width_test,
            slength_length_test=slength_length_test,
            sdiameter_diameter_test=sdiameter_diameter_test,
            slength_match=Greatest('slength_width_test', 'slength_length_test'),
            max_match=Round((F('slength_match') + F('sdiameter_diameter_test')) / 2)).distinct()

    else:
        queryset_qobjects = Product.objects.filter(*qobjects).order_by().distinct()

    return queryset_qobjects, max_match


def find_perfect_match(requested_amount, queryset, product):
    """
    Function that returns a queryset of boxes that fit the requested amount of products
    :param requested_amount: number of products
    :param queryset: a list of Box objects from the database
    :param product: product object that needs to fit in a box
    :return:
    """

    # initialize empty queryset with matching boxes
    list_of_ids = []

    # iterate over all boxes in queryset and append if match is made
    for box_object in queryset:

        amount_in_box = 0
        if box_object.inner_dim1 and box_object.inner_dim2 and box_object.inner_dim3:
            amount_in_box = product.max_in_box(box_object.inner_dim1,
                                               box_object.inner_dim2,
                                               box_object.inner_dim3)[0][0]
        elif box_object.inner_dim1 and box_object.inner_dim2 and box_object.inner_variable_dimension_MAX:
            amount_in_box = product.max_in_box(box_object.inner_dim1,
                                               box_object.inner_dim2,
                                               box_object.inner_variable_dimension_MAX)[0][0]

        # create a queryset containing matching boxes
        if amount_in_box == requested_amount:
            list_of_ids.append(box_object.id)

    success_boxes = queryset.filter(id__in=list_of_ids)

    return success_boxes


def create_queryset_product_fit(request, form, context):
    width = form.cleaned_data.get('product_width')
    length = form.cleaned_data.get('product_length')
    height = form.cleaned_data.get('product_height')
    diameter = form.cleaned_data.get('product_diameter')
    amount_of_products = form.cleaned_data.get('amount_of_products_in_box')
    cylindrical = form.cleaned_data.get('rectangular_cylindrical')
    no_tipping = form.cleaned_data.get('no_tipping')
    no_stacking = form.cleaned_data.get('no_stacking')

    # Calculate estimate of product volume for initial box selection
    if cylindrical:
        product_volume = diameter ** 2 * height / 1000000.0
        product = CylindricalProduct(diameter, height, no_tipping, no_stacking)
    else:
        product_volume = width * length * height / 1000000.0
        product = RectangularProduct(width, length, height, no_tipping, no_stacking)

    colors = request.GET.getlist('color')
    wall_thicknesses = request.GET.getlist('wall_thickness')
    standard_size = request.GET.getlist('standard_size')
    bottles = request.GET.getlist('bottles')
    product_types = [product_type for product_type in request.GET.getlist('product_type') if product_type]
    companies = request.GET.getlist('company')

    qobjects = []

    # Show liked boxes
    only_liked_boxes = request.GET.get('liked')
    no_saved_boxes_message = '<h4>Je hebt nog geen dozen bewaard om te vergelijken!</h4><p> Doe hierboven een zoekopdracht en bewaar dozen met de "bewaarknop".</p>'
    if only_liked_boxes:
        saved_boxes = request.session.get('saved_boxes')
        if saved_boxes:
            qsaved = Q(pk__in=saved_boxes)
            if not len(saved_boxes):
                context['saved_boxes_message'] = no_saved_boxes_message
        else:
            context['saved_boxes_message'] = no_saved_boxes_message
            qsaved = Q(pk__in=[])

        qobjects.append(qsaved)

    # Q objects query
    if colors:
        qcolors = Q(color__in=colors)
        qobjects.append(qcolors)

    if wall_thicknesses:
        qwall_thicknesses = Q(wall_thickness__in=wall_thicknesses)
        qobjects.append(qwall_thicknesses)

    qmain_category = Q(product_type__main_category__category_id__in=range(1, 11))
    qobjects.append(qmain_category)

    if len(product_types):
        qproduct_types = Q(product_type__product_type_id__in=product_types)
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

    # Set box volume benchmark
    error_margin = 30
    qvolume = Q(volume__range=((product_volume * amount_of_products) - error_margin * product_volume,
                               (product_volume * amount_of_products) + error_margin * product_volume))

    qobjects.append(qvolume)

    # Create Queryset
    queryset_qobjects = Product.objects.filter(
        *qobjects
    ).order_by().distinct()
    #
    # queryset_qobjects = queryset_qobjects.annotate(
    #     volume_calculated=calculate_volume).filter(qvolume)

    # Find perfect boxes in queryset boxes
    queryset_qobjects = find_perfect_match(amount_of_products, queryset_qobjects, product)

    max_match_possible = False

    return queryset_qobjects, max_match_possible


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

    return queryset


def create_filters(request, context, queryset, browse=False):
    no_filter = [('', 'x')]

    if request.GET.get('initial_search') or browse:

        request.session['filter_product_type'] = no_filter + list(
            ProductType.objects.filter(product__in=queryset).values_list('product_type_id', 'type').distinct())

        # Remove variable height boxes from product type filter
        if (115, 'variabele hoogte dozen') in request.session['filter_product_type']:
            request.session['filter_product_type'].remove((115, 'variabele hoogte dozen'))

        request.session['filter_color'] = no_filter + list(
            Color.objects.filter(product__in=queryset).values_list('id', 'color').distinct())
        request.session['filter_wall_thickness'] = no_filter + list(
            WallThickness.objects.filter(product__in=queryset).values_list('id',
                                                                           'wall_thickness').distinct())
        request.session['filter_standard_size'] = no_filter + [(value, value) for value in
                                                               queryset.filter(
                                                                   standard_size__isnull=False).order_by(
                                                                   'standard_size').values_list(
                                                                   'standard_size', flat=True).distinct()]
        request.session['filter_bottles'] = no_filter + [(value, value) for value in
                                                         queryset.filter(
                                                             bottles__isnull=False).order_by(
                                                             'bottles').values_list('bottles',
                                                                                    flat=True).distinct()]
        request.session['filter_company'] = no_filter + list(
            Company.objects.filter(product__in=queryset).values_list('id', 'company').distinct())

        # Add initial search data to session. Used for clear all filter
        request.session['initial_search_data'] = {query: value for query, value in request.GET.items() if
                                                  not query == 'initial_search'}

        # Add minimum and maximum dimensions of initial results to session. Used to refine results on size
        min_max_dimensions = get_min_max_dimensions(queryset)
        request.session['min_width'] = min_max_dimensions['min_width']
        request.session['max_width'] = min_max_dimensions['max_width']
        request.session['min_length'] = min_max_dimensions['min_length']
        request.session['max_length'] = min_max_dimensions['max_length']
        request.session['min_height'] = min_max_dimensions['min_height']
        request.session['max_height'] = min_max_dimensions['max_height']

    # todo Make aggregation that counts all filter product amounts in a single query

    filters = ['product_type__product_type_id', 'color', 'wall_thickness', 'standard_size', 'bottles', 'company']
    all_filter_values = queryset.order_by().values_list(*filters)

    filters_value_lists = [set([value
                                for value
                                in value_list
                                if value])
                           for value_list
                           in zip(*all_filter_values)]

    remaining_filters = []
    for index in range(len(filters_value_lists)):
        for value in filters_value_lists[index]:
            remaining_filters.append((value, filters[index]))

    count_dictionary = {field: {} for field in filters}
    remaining_fields = set()
    for filter in remaining_filters:
        remaining_fields.add(filter[1])
    for field in remaining_fields:
        count_queryset = queryset.values(field).order_by(field).annotate(the_count=Count(field))
        for object in count_queryset:
            count_dictionary[field][object[field]] = object['the_count']

    # Add filters to context, first check if filter keys are still in session
    context['filters'] = {}
    if 'filter_product_type' in request.session:
        context['filters'] = {
            'Product types': create_filter_list2(Filter2, request, 'product_type__product_type_id',
                                                 request.session['filter_product_type'], remaining_filters,
                                                 count_dictionary),
            'Kwaliteit': create_filter_list2(Filter2, request, 'wall_thickness',
                                             request.session['filter_wall_thickness'], remaining_filters,
                                             count_dictionary),
            'Kleuren': create_filter_list2(Filter2, request, 'color', request.session['filter_color'],
                                           remaining_filters, count_dictionary),
            'Standaard formaat': create_filter_list2(Filter2, request, 'standard_size',
                                                     request.session['filter_standard_size'],
                                                     remaining_filters, count_dictionary),
            'Aantal flessen': create_filter_list2(Filter2, request, 'bottles',
                                                  request.session['filter_bottles'], remaining_filters,
                                                  count_dictionary),
            'Producenten': create_filter_list2(Filter2, request, 'company',
                                               request.session['filter_company'], remaining_filters, count_dictionary),
        }
        # Add delete all filters to context
        if len(request.session['filter_product_type']) > 1:  # This means we have filterable results
            context['filterable_results'] = True  # Variable used in template
            context['clear_all_filters_url'] = request.path + '?' + urlencode(
                request.session['initial_search_data'])

        # Add size filter dimensions to context
        for dimension in ['min_width', 'max_width', 'min_length', 'max_length', 'min_height', 'max_height']:
            context[dimension] = request.session[dimension]

        # Add initial latest request parameters to context to add to afmetingen filter form
        parameter_dict = defaultdict(list)
        for param, value in request.GET.lists():
            if param != 'initial_search' and param != 'filter_width' and param != 'filter_length' and param != 'filter_height':
                parameter_dict[param] += value

        parameter_dict.default_factory = None  # This makes sure Django template can iterate over defaultdict

        context['size_filter_get_parameters'] = parameter_dict

    context['filter_count'] = 0
    for filter_list in context['filters'].values():
        for filter in filter_list:
            if filter.checked == True:
                context['filter_count'] += 1

    context['products_found'] = len(queryset)


def get_min_max_dimensions(queryset):
    """
    Takes a Product queryset and returns the minimum and maximum width, length and height
    :param queryset: Product class queryset
    :return: min and max of width, length and height
    """

    aggregation = queryset.aggregate(
        min_width=Min('inner_dim1'),
        max_width=Max('inner_dim1'),
        min_length=Min('inner_dim2'),
        max_length=Max('inner_dim2'),
        min_dim3=Min('inner_dim3'),
        min_var_height=Min('inner_variable_dimension_MIN'),
        max_dim3=Max('inner_dim3'),
        max_var_height=Max('inner_variable_dimension_MAX')
    )

    # Determine maximum height
    if aggregation.get('max_var_height') and aggregation.get('max_dim3'):
        if aggregation['max_dim3'] >= aggregation['max_var_height']:
            aggregation['max_height'] = aggregation['max_dim3']
        else:
            aggregation['max_height'] = aggregation['max_var_height']
    elif aggregation.get('max_dim3') and not aggregation.get('max_var_height'):
        aggregation['max_height'] = aggregation['max_dim3']
    else:
        aggregation['max_height'] = aggregation['max_var_height']

    # Determine minimum height
    if aggregation.get('min_var_height') and aggregation.get('min_dim3'):
        aggregation['min_height'] = aggregation['min_dim3'] if aggregation['min_dim3'] <= aggregation[
            'min_var_height'] else aggregation['min_var_height']
    elif aggregation.get('min_dim3') and not aggregation.get('min_var_height'):
        aggregation['min_height'] = aggregation['min_dim3']
    else:
        aggregation['min_height'] = aggregation['min_var_height']

    return aggregation
