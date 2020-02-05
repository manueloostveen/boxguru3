from urllib.parse import urlencode

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.views import generic
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from products.models import Product, WallThickness, Color, ProductType, Company
from .forms import SearchProductForm, SearchBoxForm, SearchTubeForm, SearchEnvelopeBagForm, FitProductForm, SignUpForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, F, Max, Case, When, ExpressionWrapper, DecimalField, Avg, Func, Count
from django.db.models.functions import Greatest, Sqrt
from products.product_categories import box_main_category_dict
from math import pi
from products.search_view_helpers import Round, Abs, Filter, Filter2, create_filter_list, create_filter_list2, \
    create_queryset, create_sort_headers, Filter3, make_pagination, order_queryset, FilterVarHeight, \
    create_queryset_product_fit, create_filters
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from products.models import MainCategory
from django.contrib.auth import login, authenticate
from .populate_db import get_parameter_to_category_product_type_id as get2cat


# Create your views here.

def index(request):
    """View function for home page of site"""

    # Generate counts of some of the  main objects
    num_products = Product.objects.count()
    num_colors = Color.objects.count()
    num_wallthickness = WallThickness.objects.count()
    num_producttype = ProductType.objects.count()
    num_test = Product.objects.filter(description__icontains='doos').count()
    num_mailbox = Product.objects.filter(product_type__type='mailbox box').count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_products': num_products,
        'num_colors': num_colors,
        'num_wallthickness': num_wallthickness,
        'num_producttype': num_producttype,
        'num_test': num_test,
        'num_mailbox': num_mailbox,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'products/index.html', context=context)


class ProductListView(generic.ListView):
    """the generic views look for templates in /application_name/the_model_name_list.html
    (products/product_list.html in this case) inside
    the application's /application_name/templates/ directory (/products/templates/)."""

    model = Product
    # context_object_name = 'my_product_list'  # your own name for the list as a template variable
    # template_name = 'products/my_arbitrary_template_name_list.html'  # Specify your own template name/location

    # def get_queryset(self):
    #     """Overriding method to alter the returned queryset. The base view
    #     standard returns all products."""
    #     # return Product.objects.all()[:5]  # Get 5 products (test)
    #
    #

    paginate_by = 10

    def get_context_data(self, **kwargs):
        """Overriding method to add arbitrary data to the context"""

        # Call the base implementation first to get the context
        context = super(ProductListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context


class ProductDetailView(generic.DetailView):
    model = Product


class ProductTypeListView(generic.ListView):
    model = ProductType


class ProductTypeDetailView(generic.DetailView):
    model = ProductType

    def get_context_data(self, **kwargs):
        context = super(ProductTypeDetailView, self).get_context_data(**kwargs)
        context['products'] = Product.objects.filter(product_type=self.get_object())
        return context


class ColorListView(generic.ListView):
    model = Color


class ColorDetailView(generic.DetailView, generic.list.MultipleObjectMixin):
    model = Color
    paginate_by = 10

    def get_context_data(self, **kwargs):
        object_list = Product.objects.filter(color=self.get_object())
        context = super(ColorDetailView, self).get_context_data(object_list=object_list, **kwargs)
        return context


class WallThicknessListView(generic.ListView):
    model = WallThickness


class WallThicknessDetailView(generic.DetailView, generic.list.MultipleObjectMixin):
    model = WallThickness
    paginate_by = 10

    def get_context_data(self, **kwargs):
        object_list = Product.objects.filter(wall_thickness=self.get_object())
        context = super(WallThicknessDetailView, self).get_context_data(object_list=object_list, **kwargs)
        return context


class GenericListView(generic.ListView):
    model = None
    template_name = 'products/generic_list.html'

    # paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super(GenericListView, self).get_context_data(
            category_name=self.model._meta.verbose_name_plural.title(), **kwargs)
        context['clsname'] = self.model.__name__
        # current_page = self.request.GET.get('page', 1)
        # if current_page != 1:
        #     current_page = f"?page={current_page}"
        #     context['current_page'] = current_page

        return context


def main_category_view(request):
    context = {}
    template_name = 'products/main_categories.html'
    context['categories'] = MainCategory.objects.all()
    return render(request, template_name, context)


def main_category_detail_view(request, pk):
    context = {}
    template_name = 'products/product_categories.html'
    product_categories = ProductType.objects.filter(main_category__id__exact=pk)

    if len(product_categories) == 1:
        return redirect(product_categories[0])

    context['product_categories'] = product_categories

    return render(request, template_name, context)


def product_type_detail_view(request, pk):
    context = {}
    template_name = 'products/product_type_detail.html'
    queryset = Product.objects.filter(product_type__id__exact=pk)
    # queryset = create_queryset(request, None, context)

    create_sort_headers(request, context)
    queryset = order_queryset(request, context, queryset)
    create_filters(request, context, queryset, browse=True)
    make_pagination(request, context, queryset)

    context['product_type'] = ProductType.objects.get(id=pk)
    return render(request, template_name, context)


class GenericDetailView(generic.DetailView, generic.list.MultipleObjectMixin):
    model = None
    paginate_by = 10
    template_name = 'products/generic_detail.html'

    def get_context_data(self, **kwargs):
        instance = self.get_object()

        if isinstance(instance, MainCategory):
            object_list = instance.producttype_set.all()
            category = 'main_category'
        elif isinstance(instance, ProductType):
            object_list = instance.product_set.all()
            category = 'product_type'

        context = super(GenericDetailView, self).get_context_data(object_list=object_list,
                                                                  category=category, **kwargs)
        return context


class LikedProductsByUserView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing liked products to current user"""
    model = Product
    template_name = 'products/product_list_liked_user.html'
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.filter(users=self.request.user)


class AllLikedProductsByUsersView(PermissionRequiredMixin, generic.ListView):
    """View to check all liked products"""
    model = Product
    template_name = 'products/product_list_liked_all.html'
    paginate_by = 10

    # set permission 'appname.permission'
    permission_required = 'products.can_see_all_liked_products'

    def get_queryset(self):
        return Product.objects.filter(users__isnull=False)


def like_product(request, pk):
    if request.method == 'POST':
        product = Product.objects.get(pk=pk)
        product.users.add(request.user.id)
        product.save()
        next = request.POST.get('next', '/')

        return HttpResponseRedirect(next)


def unlike_product(request, pk):
    if request.method == 'POST':
        product = Product.objects.get(pk=pk)
        product.users.remove(request.user.id)
        product.save()
        next = request.POST.get('next', '/')

        return HttpResponseRedirect(next)


def search_product_OLD(request):
    context = {}
    template_name = 'products/search_products.html'

    if request.method == 'GET':

        # Sorting headers
        order_by = request.GET.get('sort')

        # Build current URL without sort parameter
        current_path = request.path
        if len(request.GET):
            current_path += '?'

        for key, values in request.GET.lists():
            if key != 'sort' and key != 'by':
                for value in values:
                    if current_path[-1] == '?':
                        param_symbol = ''
                    else:
                        param_symbol = '&'
                    current_path += param_symbol + key + "=" + value

        # Swapper dictionary to set order to Ascending or Descending
        ordering_swapper = {
            'ASC': 'DESC',
            'DESC': 'ASC'
        }

        # ordering dict to choose direction based on order_by ('sort') parameter
        ordering_dict = {
            order_by: ordering_swapper[request.GET.get('by', 'DESC')]
        }

        # Build sorting headers and add to context
        if current_path[-1] == "/":
            param_symbol = "?"
        else:
            param_symbol = "&"

        context[
            'category_header'] = current_path + param_symbol + "sort=product_type" + f'&by={ordering_dict.get("product_type", "DESC")}'
        context[
            'width_header'] = current_path + param_symbol + "sort=inner_dim1" + f'&by={ordering_dict.get("inner_dim1", "ASC")}'
        context[
            'length_header'] = current_path + param_symbol + "sort=inner_dim2" + f'&by={ordering_dict.get("inner_dim2", "ASC")}'
        context[
            'height_header'] = current_path + param_symbol + "sort=inner_dim3" + f'&by={ordering_dict.get("inner_dim3", "ASC")}'
        context[
            'diameter_header'] = current_path + param_symbol + "sort=diameter" + f'&by={ordering_dict.get("diameter", "ASC")}'
        context[
            'match_header'] = current_path + param_symbol + "sort=max_match" + f'&by={ordering_dict.get("max_match", "ASC")}'
        context[
            'wall_thickness_header'] = current_path + param_symbol + "sort=wall_thickness" + f'&by={ordering_dict.get("wall_thickness", "ASC")}'
        context[
            'color_header'] = current_path + param_symbol + "sort=color" + f'&by={ordering_dict.get("color", "DESC")}'
        context[
            'standard_size_header'] = current_path + param_symbol + "sort=standard_size" + f'&by={ordering_dict.get("standard_size", "ASC")}'
        context[
            'bottles_header'] = current_path + param_symbol + "sort=bottles" + f'&by={ordering_dict.get("bottles", "ASC")}'

        context[
            'lowest_price_header'] = current_path + param_symbol + "sort=lowest_price" + f'&by={ordering_dict.get("lowest_price", "DESC")}'
        context[
            'price_header'] = current_path + param_symbol + "sort=price_ex_BTW" + f'&by={ordering_dict.get("price_ex_BTW", "DESC")}'

        # Set  ordering
        if order_by:
            # Prepend "-" if order is Ascending
            if request.GET.get('by') == "ASC":
                order_by = "-" + order_by
        else:
            order_by = '-max_match'

        # Check GET request if and what type of form is requested
        if request.GET.get('box-form') or request.GET.get('tube-form') or request.GET.get('envelope-form'):
            if request.GET.get('box-form'):
                context['box_form'] = SearchBoxForm(request.GET)
                context['tube_form'] = SearchTubeForm()
                context['envelope_form'] = SearchEnvelopeBagForm()
                request.session['searched'] = 'box'
                context['searched'] = 'box'

            elif request.GET.get('tube-form'):
                context['box_form'] = SearchBoxForm()
                context['tube_form'] = SearchTubeForm(request.GET)
                context['envelope_form'] = SearchEnvelopeBagForm()
                request.session['searched'] = 'tube'
                context['searched'] = 'tube'

            elif request.GET.get('envelope-form'):
                tube_form = SearchTubeForm()
                box_form = SearchBoxForm()
                envelope_form = SearchEnvelopeBagForm(request.GET)
                context['box_form'] = box_form
                context['tube_form'] = tube_form
                context['envelope_form'] = envelope_form
                request.session['searched'] = 'envelope'
                context['searched'] = 'envelope'

            # save form data in session
            request.session['width'] = request.GET.get('width')
            request.session['length'] = request.GET.get('length')
            request.session['height'] = request.GET.get('height')
            request.session['diameter'] = request.GET.get('diameter')
            request.session['main_categories'] = request.GET.getlist('main_categories')
            request.session['categories'] = request.GET.getlist('categories')
            request.session['wall_thicknesses'] = request.GET.getlist('wall_thicknesses')
            request.session['colors'] = request.GET.getlist('colors')

        # If no form in request, then landed via redirect. Check session for searched parameter
        elif request.session.get('searched') == 'box':
            data = {
                'width': request.session['width'],
                'length': request.session['length'],
                'height': request.session['height'],
                'main_categories': request.session['main_categories'],
                'wall_thicknesses': request.session['wall_thicknesses'],
                'colors': request.session['colors']
            }
            context['box_form'] = SearchBoxForm(data)
            context['tube_form'] = SearchTubeForm()
            context['envelope_form'] = SearchEnvelopeBagForm()

        elif request.session.get('searched') == 'tube':
            data = {
                'length': request.session['length'],
                'diameter': request.session['diameter'],
                'categories': request.session['categories'],
                'wall_thicknesses': request.session['wall_thicknesses'],
                'colors': request.session['colors'],
            }
            context['box_form'] = SearchBoxForm()
            context['tube_form'] = SearchTubeForm(data)
            context['envelope_form'] = SearchEnvelopeBagForm()

        elif request.session.get('searched') == 'envelope':
            data = {
                'width': request.session['width'],
                'length': request.session['length'],
                'categories': request.session['categories'],
                'colors': request.session['colors']
            }
            context['box_form'] = SearchBoxForm()
            context['tube_form'] = SearchTubeForm()
            context['envelope_form'] = SearchEnvelopeBagForm(data)

        else:
            context['box_form'] = SearchBoxForm()
            context['tube_form'] = SearchTubeForm()
            context['envelope_form'] = SearchEnvelopeBagForm()
            context['no_search'] = True

    # Create form
    if request.session.get('searched') == 'box':
        form = context['box_form']
    elif request.session.get('searched') == 'tube':
        form = context['tube_form']
    elif request.session.get('searched') == 'envelope':
        form = context['envelope_form']
    else:
        form = None

    if form:
        if form.is_valid():

            width = form.cleaned_data.get('width')
            length = form.cleaned_data.get('length')
            height = form.cleaned_data.get('height')
            diameter = form.cleaned_data.get('diameter')
            colors = form.cleaned_data.get('colors')
            wall_thicknesses = form.cleaned_data.get('wall_thicknesses')
            main_categories = form.cleaned_data.get('main_categories')
            categories = form.cleaned_data.get('categories')

            # Q objects checkboxes
            if colors:
                qcolors = Q(color__in=colors)
            else:
                qcolors = Q()

            if wall_thicknesses:
                qwall_thicknesses = Q(wall_thickness__in=wall_thicknesses)
            else:
                qwall_thicknesses = Q()

            if main_categories:
                qproduct_types = Q(product_type__main_category__in=main_categories)
            elif categories:
                qproduct_types = Q(product_type__in=categories)

            error_margin = 50
            error_margin_diameter = 15

            # Q objects search fields
            qwidth_length = Q()
            qheight = Q()
            qdiameter = Q()

            if width and not length:
                width = float(width)
                qwidth_length = Q(inner_dim1__range=(width - error_margin, width + error_margin)) | Q(
                    inner_dim2__range=(width - error_margin, width + error_margin))

            elif length and not width:
                length = float(length)
                qwidth_length = Q(inner_dim2__range=(length - error_margin, length + error_margin)) | Q(
                    inner_dim1__range=(length - error_margin, length + error_margin))

            elif width and length:
                width = float(width)
                length = float(length)
                qwidth_length = (Q(inner_dim1__range=(width - error_margin, width + error_margin)) & Q(
                    inner_dim2__range=(length - error_margin, length + error_margin))) | (
                                        Q(inner_dim2__range=(width - error_margin, width + error_margin)) & Q(
                                    inner_dim1__range=(length - error_margin, length + error_margin)))

            if height:
                height = float(height)
                qheight = Q(inner_dim3__range=(height - error_margin, height + error_margin)) | (
                    (Q(inner_variable_dimension_MAX__gte=height) & Q(inner_variable_dimension_MIN__lte=height)))

            if diameter:
                diameter = float(diameter)
                qdiameter = Q(diameter__range=(diameter - error_margin_diameter, diameter + error_margin_diameter))

            # list qobject for *args
            qobjects = [qcolors,
                        qwall_thicknesses,
                        qproduct_types, qwidth_length,
                        qheight, qdiameter
                        ]

            # Create round function, arity 1 so rounds to 0 decimals, no input needed
            class Round(Func):
                function = 'ROUND'
                arity = 1

            # Create absolute function
            class Abs(Func):
                function = 'ABS'

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
                ).annotate(
                    swidth_width_test=swidth_width_test).annotate(
                    swidth_length_test=swidth_length_test).annotate(
                    max_match=Round(Greatest('swidth_width_test', 'swidth_length_test'))).order_by(order_by)


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
                ).annotate(
                    slength_width_test=slength_width_test).annotate(
                    slength_length_test=slength_length_test).annotate(
                    max_match=Round(Greatest('slength_width_test', 'slength_length_test'))).order_by(order_by)


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
                ).annotate(
                    slength_width_test=slength_width_test).annotate(
                    slength_length_test=slength_length_test).annotate(
                    swidth_width_test=swidth_width_test).annotate(
                    swidth_length_test=swidth_length_test).annotate(
                    sww_sll_match=(F('swidth_width_test') + F('slength_length_test')) / 2).annotate(
                    swl_slw_match=(F('swidth_length_test') + F('slength_width_test')) / 2).annotate(
                    max_match=Round(Greatest('sww_sll_match', 'swl_slw_match'))).order_by(order_by)


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
                ).annotate(
                    slength_width_test=slength_width_test).annotate(
                    slength_length_test=slength_length_test).annotate(
                    swidth_width_test=swidth_width_test).annotate(
                    swidth_length_test=swidth_length_test).annotate(
                    sheight_height_test=sheight_height_test).annotate(
                    sww_sll_match=(F('swidth_width_test') + F('slength_length_test')) / 2).annotate(
                    swl_slw_match=(F('swidth_length_test') + F('slength_width_test')) / 2).annotate(
                    wl_match=Greatest('sww_sll_match', 'swl_slw_match')).annotate(
                    max_match=Round((F('wl_match') * 2 + F('sheight_height_test')) / 3)).order_by(order_by)

            elif diameter and not length:
                sdiameter_diameter_test = Case(
                    When(diameter__isnull=False,
                         then=(100 - (Abs(F('diameter') - diameter) / F('diameter')) * 100.0)),
                    default=0, output_field=DecimalField()
                )
                queryset_qobjects = Product.objects.filter(
                    *qobjects
                ).annotate(
                    max_match=Round(sdiameter_diameter_test)).order_by(order_by)

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
                ).annotate(
                    slength_width_test=slength_width_test).annotate(
                    slength_length_test=slength_length_test).annotate(
                    sdiameter_diameter_test=sdiameter_diameter_test).annotate(
                    slength_match=Greatest('slength_width_test', 'slength_length_test')).annotate(
                    max_match=Round((F('slength_match') + F('sdiameter_diameter_test')) / 2)).order_by(order_by)


            else:
                if 'max_match' not in order_by:
                    queryset_qobjects = Product.objects.filter(*qobjects).order_by(order_by)
                else:
                    queryset_qobjects = Product.objects.filter(*qobjects).order_by('product_type')

            # Create  querysets for result filter
            context['filter_producttypes'] = ProductType.objects.filter(product__in=queryset_qobjects).distinct()
            context['filter_colors'] = Color.objects.filter(product__in=queryset_qobjects).distinct()
            context['filter_wallthicknesses'] = WallThickness.objects.filter(product__in=queryset_qobjects).distinct()
            context['filter_standard_size'] = queryset_qobjects.filter(standard_size__isnull=False).order_by(
                'standard_size').values_list('standard_size', flat=True).distinct()
            bottles_query = queryset_qobjects.filter(bottles__isnull=False).order_by('bottles').values_list('bottles',
                                                                                                            flat=True).distinct()
            context['filter_bottles'] = [str(bottles) + " fles" if bottles == 1 else str(bottles) + " flessen" for
                                         bottles in bottles_query]

            # Add search params to context
            context['search_width'] = width
            context['search_length'] = length
            context['search_height'] = height
            context['search_diameter'] = diameter
            context['queryset'] = queryset_qobjects
            context['model'] = Product
            context['order_by'] = order_by

    return render(request, template_name, context)

def home(request):
    context = {}
    template_name = 'products/home.html'

    if request.method == 'GET':
        context['box_form'] = SearchBoxForm()
        context['fit_product_form'] = FitProductForm()
        context['boxes'] = Product.objects.filter(product_type__main_category__category_id__in=range(1,11)).count()
        context['companies'] = Company.objects.count()
        print(context['boxes'], context['companies'])

    return render(request, template_name, context)




def search_product(request, test=None, category_name=None):
    context = {}
    template_name = 'products/search_products.html'

    if request.method == 'GET':

        product_type_footer = None
        browse = False
        if category_name:
            category, product_type_footer = get2cat[category_name]
            browse = True
            form = SearchBoxForm({'category': category})
            context['box_form'] = form
            context['fit_product_form'] = FitProductForm()
            context['category_name'] = category_name

        elif 'form' in request.GET:
            if request.GET['form'] == 'box':
                context['box_form'] = SearchBoxForm(request.GET)
                context['fit_product_form'] = FitProductForm()
                context['searched'] = 'box'
                form = context['box_form']

            elif request.GET['form'] == 'fitbox':
                context['fit_product_form'] = FitProductForm(request.GET)
                context['searched'] = 'fitbox'
                form = context['fit_product_form']

        else:
            # Check GET request if and what type of form is requested
            form = None
            context['box_form'] = SearchBoxForm()
            context['fit_product_form'] = FitProductForm()
            context['no_search'] = True

        if form:
            if form.is_valid():

                # Create queryset, normal search or fitbox search
                if isinstance(form, FitProductForm):
                    queryset_qobjects, max_match_possible = create_queryset_product_fit(request, form, context)

                else:
                    queryset_qobjects, max_match_possible = create_queryset(request, form, context, initial_product_type=product_type_footer)

                # Filter queryset based on "Afmetingen" filter
                if request.GET.get('filter_width'):
                    min_width = request.GET.get('filter_width').split(';')[0]
                    max_width = request.GET.get('filter_width').split(';')[1]
                    min_length = request.GET.get('filter_length').split(';')[0]
                    max_length = request.GET.get('filter_length').split(';')[1]
                    min_height = request.GET.get('filter_height').split(';')[0]
                    max_height = request.GET.get('filter_height').split(';')[1]

                    context['filter_min_width'] = min_width
                    context['filter_max_width'] = max_width
                    context['filter_min_length'] = min_length
                    context['filter_max_length'] = max_length
                    context['filter_min_height'] = min_height
                    context['filter_max_height'] = max_height

                    qheight = Q(inner_dim3__range=(min_height, max_height)) | (
                        (Q(inner_variable_dimension_MAX__gte=min_height) & Q(
                            inner_variable_dimension_MIN__lte=max_height)))

                    qwidth_length = (Q(inner_dim1__range=(min_width, max_width)) & Q(
                        inner_dim2__range=(min_length, max_length))) | (
                                            Q(inner_dim2__range=(min_width, max_width)) & Q(
                                        inner_dim1__range=(min_length, max_length)))

                    queryset_qobjects = queryset_qobjects.filter(
                        qheight,
                        qwidth_length
                    )

                # Set  ordering
                queryset_qobjects = order_queryset(request, context, queryset_qobjects,
                                                   max_match_possible=max_match_possible)

                # # Add sort link for order button and sort direction variable to context
                # context['sort_order_link'], context['sort'] = create_sort_order_link(request, order_by)

                # Add sorting headers to context
                create_sort_headers(request, context)

                # Create filters
                create_filters(request, context, queryset_qobjects, browse=browse)

                # Pagination
                make_pagination(request, context, queryset_qobjects)

                context['products_found'] = len(queryset_qobjects)

    return render(request, template_name, context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('search-product')
    else:
        form = SignUpForm()
    return render(request, 'products/signup.html', {'form': form})


class ProductCreate(PermissionRequiredMixin, CreateView):
    # template_name_suffix = '_other_suffix' default template is: model_name_form.html
    model = Product
    fields = '__all__'
    permission_required = 'products.create_update_delete'
    # def get_form(self, form_class=None):
    #     form = super(ProductCreate, self).get_form(form_class)
    #     form.fields['']


class ProductUpdate(PermissionRequiredMixin, UpdateView):
    model = Product
    fields = '__all__'
    permission_required = 'products.create_update_delete'


class ProductDelete(PermissionRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('products')
    permission_required = 'products.create_update_delete'


def bootstrap(request):
    context = {}
    template_name = 'products/bootstrap2.html'
    context['queryset'] = Product.objects.all()
    return render(request, template_name, context)
