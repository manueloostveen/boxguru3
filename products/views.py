from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from products.models import Product, WallThickness, Color, ProductType
from .forms import SearchProductForm, SearchBoxForm, SearchTubeForm, SearchEnvelopeBagForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, F, Max, Case, When, ExpressionWrapper, DecimalField, Avg, Func
from django.db.models.functions import Greatest, Sqrt

from math import pi

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
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super(GenericListView, self).get_context_data(
            category_name=self.model._meta.verbose_name_plural.title(), **kwargs)
        context['clsname'] = self.model.__name__
        current_page = self.request.GET.get('page', 1)
        if current_page != 1:
            current_page = f"?page={current_page}"
            context['current_page'] = current_page

        return context


class GenericDetailView(generic.DetailView, generic.list.MultipleObjectMixin):
    model = None
    paginate_by = 10
    template_name = 'products/generic_detail.html'

    def get_context_data(self, **kwargs):
        instance = self.get_object()

        object_list = instance.product_set.all()
        context = super(GenericDetailView, self).get_context_data(object_list=object_list, **kwargs)
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


def search_product(request):
    context = {}
    template_name = 'products/search_products.html'

    if request.method == 'GET':

        if request.GET.get('box-form') or request.GET.get('tube-form') or request.GET.get('envelope-form'):
            if request.GET.get('box-form'):
                box_form = SearchBoxForm(request.GET)
                tube_form = SearchTubeForm()
                envelope_form = SearchEnvelopeBagForm()
                context['box_form'] = box_form
                context['tube_form'] = tube_form
                context['envelope_form'] = envelope_form
                request.session['searched'] = 'box'
                context['searched'] = 'box'

            elif request.GET.get('tube-form'):
                tube_form = SearchTubeForm(request.GET)
                box_form = SearchBoxForm()
                envelope_form = SearchEnvelopeBagForm()
                context['box_form'] = box_form
                context['tube_form'] = tube_form
                context['envelope_form'] = envelope_form
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

        elif request.session.get('searched') == 'box':
            data = {
                'width': request.session['width'],
                'length': request.session['length'],
                'height': request.session['height'],
                'main_categories': request.session['main_categories'],
                'wall_thicknesses': request.session['wall_thicknesses'],
                'colors': request.session['colors']
            }
            box_form = SearchBoxForm(data)
            tube_form = SearchTubeForm()
            envelope_form = SearchEnvelopeBagForm()
            context['box_form'] = box_form
            context['tube_form'] = tube_form
            context['envelope_form'] = envelope_form

        elif request.session.get('searched') == 'tube':
            data = {
                'length': request.session['length'],
                'diameter': request.session['diameter'],
                'categories': request.session['categories'],
                'wall_thicknesses': request.session['wall_thicknesses'],
                'colors': request.session['colors'],
            }
            tube_form = SearchTubeForm(data)
            box_form = SearchBoxForm()
            envelope_form = SearchEnvelopeBagForm()
            context['box_form'] = box_form
            context['tube_form'] = tube_form
            context['envelope_form'] = envelope_form

        elif request.session.get('searched') == 'envelope':
            data = {
                'width': request.session['width'],
                'length': request.session['length'],
                'categories': request.session['categories'],
                'colors': request.session['colors']
            }
            envelope_form = SearchEnvelopeBagForm(data)
            box_form = SearchBoxForm()
            tube_form = SearchTubeForm()
            context['box_form'] = box_form
            context['tube_form'] = tube_form
            context['envelope_form'] = envelope_form

        else:
            # Search box form
            box_form = SearchBoxForm()
            tube_form = SearchTubeForm()
            envelope_form = SearchEnvelopeBagForm()
            context['box_form'] = box_form
            context['tube_form'] = tube_form
            context['envelope_form'] = envelope_form
            context['no_search'] = True

    # Create form
    if request.session.get('searched') == 'box':
        form = box_form
    elif request.session.get('searched') == 'tube':
        form = tube_form
    elif request.session.get('searched') == 'envelope':
        form = envelope_form
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
                    When(inner_dim1__isnull=False, then=(100 - Abs((F('inner_dim1') - width) / F('inner_dim1')) * 100.0)),
                    default=0, output_field=DecimalField()
                )
                swidth_length_test = Case(
                    When(inner_dim2__isnull=False, then=(100 - Abs((F('inner_dim2') - width) / F('inner_dim2')) * 100.0)),
                    default=0, output_field=DecimalField()
                )
                queryset_qobjects = Product.objects.filter(
                    *qobjects
                ).annotate(
                    swidth_width_test=swidth_width_test).annotate(
                    swidth_length_test=swidth_length_test).annotate(
                    max_match=Round(Greatest('swidth_width_test', 'swidth_length_test'))).order_by('-max_match')


            elif length and not width and not height:

                slength_width_test = Case(
                    When(inner_dim1__isnull=False, then=(100 - (Abs(F('inner_dim1') - length) / F('inner_dim1')) * 100.0)),
                    default=0, output_field=DecimalField()
                )
                slength_length_test = Case(
                    When(inner_dim2__isnull=False, then=(100 - (Abs(F('inner_dim2') - length) / F('inner_dim2')) * 100.0)),
                    default=0, output_field=DecimalField()
                )

                queryset_qobjects = Product.objects.filter(
                    *qobjects
                ).annotate(
                    slength_width_test=slength_width_test).annotate(
                    slength_length_test=slength_length_test).annotate(
                    max_match=Round(Greatest('slength_width_test', 'slength_length_test'))).order_by('-max_match')


            elif length and width and not height:

                swidth_width_test = Case(
                    When(inner_dim1__isnull=False, then=(100 - (Abs(F('inner_dim1') - width) / F('inner_dim1')) * 100.0)),
                    default=0, output_field=DecimalField()
                )
                swidth_length_test = Case(
                    When(inner_dim2__isnull=False, then=(100 - (Abs(F('inner_dim2') - width) / F('inner_dim2')) * 100.0)),
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
                    max_match=Round(Greatest('sww_sll_match', 'swl_slw_match'))).order_by('-max_match')


            elif width and length and height:

                swidth_width_test = Case(
                    When(inner_dim1__isnull=False, then=(100 - (Abs(F('inner_dim1') - width) / F('inner_dim1')) * 100.0)),
                    default=0, output_field=DecimalField()
                )
                swidth_length_test = Case(
                    When(inner_dim2__isnull=False, then=(100 - (Abs(F('inner_dim2') - width) / F('inner_dim2')) * 100.0)),
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
                         then=(100 - (Func((F('inner_dim3') - length), function='ABS') / F('inner_dim3')) * 100.0)),
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
                    max_match=Round((F('wl_match') * 2 + F('sheight_height_test')) / 3)).order_by('-max_match')

            elif length and diameter:

                volume_test = Case(

                )
                pass

            else:
                queryset_qobjects = Product.objects.filter(*qobjects)

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
            context['products_found'] = len(queryset_qobjects)
            context['model'] = Product

    return render(request, template_name, context)


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
