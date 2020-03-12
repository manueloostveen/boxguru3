
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

from products.models import Product, WallThickness, Color, ProductType, Company
from .forms import SearchBoxForm, SearchTubeForm, SearchEnvelopeBagForm, FitProductForm, SignUpForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, F, Case, When, DecimalField, Func
from django.db.models.functions import Greatest

from products.search_view_helpers import create_queryset, create_sort_headers, make_pagination, order_queryset, create_queryset_product_fit, create_filters, FilterLikedBoxes
from products.models import MainCategory
from django.contrib.auth import login, authenticate
from .populate_db import get_parameter_to_category_product_type_id as get2cat, \
    get_parameter_to_main_category_id as get2main_cat, box_main_categories_clean
from products.category_texts import main_category_texts

import json


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
    context['categories'] = MainCategory.objects.all().order_by('-category')
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


def home(request):
    context = {}
    template_name = 'products/home.html'

    # Initialize session
    request.session['welcome'] = True

    # Add category texts to context
    context['category_texts'] = main_category_texts

    # Add companies string to context
    companies = Company.objects.all()
    company_string = ''
    first = True
    idx_last_company = len(companies) - 1
    for idx, company in enumerate(companies):
        if first:
            company_string += company.company
            first = False
        elif idx == idx_last_company:
            company_string += " & " + company.company
        else:
            company_string += ", " + company.company

    context['company_string'] = company_string

    if request.method == 'GET':
        context['box_form'] = SearchBoxForm()
        context['fit_product_form'] = FitProductForm()
        context['boxes'] = Product.objects.filter(product_type__main_category__category_id__in=range(1, 11)).count()
        context['companies'] = Company.objects.count()
        context['force_show_categories'] = True

    return render(request, template_name, context)

def doos_op_maat(request):
    context = {}
    template_name = 'products/doos_op_maat.html'

    if request.method == 'GET':
        context['box_form'] = SearchBoxForm()
        context['fit_product_form'] = FitProductForm()
        context['force_show_categories'] = True

    return render(request, template_name, context)


def search_product(request, category_name=None,
                   hoofdcategorie=None,
                   subcategorie=None,
                   ):
    context = {}
    template_name = 'products/search_products.html'
    context['category_texts'] = main_category_texts

    # template errors fix
    context['show_initial_subcategory'] = None
    context['show_initial_category'] = None

    if request.method == 'GET':

        product_type_footer = None
        main_category_footer = None
        browse = False
        form = None

        if subcategorie and hoofdcategorie:
            category, product_type_footer, nice_name = get2cat[subcategorie]
            _, nice_name_hoofdcat = get2main_cat[hoofdcategorie]
            browse = subcategorie
            form = SearchBoxForm({'category': category})
            context['box_form'] = form
            context['fit_product_form'] = FitProductForm()
            context['category_name'] = nice_name
            context['show_initial_category'] = category
            context['show_initial_subcategory'] = product_type_footer
            context['breadcrumb'] = hoofdcategorie, nice_name_hoofdcat

        elif hoofdcategorie:
            main_category_footer, nice_name = get2main_cat[hoofdcategorie]
            browse = hoofdcategorie
            form = SearchBoxForm({'category': main_category_footer})
            context['box_form'] = form
            context['fit_product_form'] = FitProductForm()
            context['category_name'] = nice_name
            context['show_initial_category'] = main_category_footer
            context['breadcrumb'] = None
            context['sub_category_links'] = box_main_categories_clean.get(hoofdcategorie)
            context['main_category_raw_parameter'] = hoofdcategorie


        elif 'form' in request.GET:
            if request.GET['form'] == 'box':
                context['box_form'] = SearchBoxForm(request.GET)
                context['fit_product_form'] = FitProductForm()
                context['searched'] = 'box'
                form = context['box_form']

            elif request.GET['form'] == 'fitbox':
                context['fit_product_form'] = FitProductForm(request.GET)
                context['box_form'] = SearchBoxForm()
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
                    queryset_qobjects, max_match_possible = create_queryset(request, form, context,
                                                                            initial_product_type=product_type_footer,
                                                                            initial_main_category=main_category_footer
                                                                            )

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
                context['liked_filter'] = FilterLikedBoxes(request)

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


def like_unlike_box(request, pk):
    if request.method == 'POST':

        next = request.POST.get('next', '/')
        response = redirect(next)

        # cookie version
        saved_boxes_json = request.COOKIES.get('saved_boxes')

        if saved_boxes_json:
            deserialized_list = json.loads(saved_boxes_json)

            if pk in deserialized_list:
                deserialized_list.remove(pk)
            else:
                deserialized_list.append(pk)

            reserialized_list = json.dumps(deserialized_list)

        else:
            saved_boxes_list = [pk]
            reserialized_list = json.dumps(saved_boxes_list)

        response.set_cookie(key='saved_boxes', value=reserialized_list, max_age=60 * 60 * 24 * 360)

        # # Sessions version
        # saved_boxes = request.session.get('saved_boxes')
        # if saved_boxes:
        #     if pk in saved_boxes:
        #         saved_boxes.remove(pk)
        #     else:
        #         saved_boxes.append(pk)
        # else:
        #     saved_boxes = [pk]
        #
        # request.session['saved_boxes'] = saved_boxes

        return response
