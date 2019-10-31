from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from products.models import Product, WallThickness, Color, ProductType
from .forms import SearchProductForm, SearchProductModelForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from itertools import chain


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

    def return_results(form):


            return render(request, template_name, context)

    if request.method == 'GET':
        context['test'] = request.GET
        old_form_data = request.session.get('form_data')

        if request.GET.get('form_test'):
            form = SearchProductForm(request.GET)
            request.session['form_data'] = request.GET
        elif old_form_data:
            form = SearchProductForm(old_form_data)
        else:
            form = SearchProductForm()

        context['form'] = form

        if form.is_valid():
            product_type = form.cleaned_data['product_type']
            color = form.cleaned_data['color']
            wall_thickness = form.cleaned_data['wall_thickness']
            width = form.cleaned_data['width']
            length = form.cleaned_data['length']
            height = form.cleaned_data['height']
            diameter = form.cleaned_data['diameter']
            error_margin = form.cleaned_data['error_margin']

            # Add search params to context
            context['search_width'] = width
            context['search_length'] = length
            context['search_height'] = height

            # Create query params
            query = {}
            if product_type:
                query['product_type'] = product_type
            if color:
                query['color'] = color
            if wall_thickness:
                query['wall_thickness'] = wall_thickness

            queryset = Product.objects.filter(**query)
            # alternative queryset to swap width and length and check diameter
            queryset_alt = Product.objects.filter(**query)

            # Query products based on w/l/h
            if width:
                queryset = queryset.filter(inner_dim1__range=(width - error_margin, width + error_margin))
                queryset_alt = queryset_alt.filter(inner_dim2__range=(width - error_margin, width + error_margin))

            if length:
                queryset = queryset.filter(inner_dim2__range=(length - error_margin, length + error_margin))
                queryset_alt = queryset_alt.filter(inner_dim1__range=(length - error_margin, length + error_margin))

            if height:
                queryset = queryset.filter(inner_dim3__range=(height - error_margin, height + error_margin))
                queryset_alt = queryset_alt.filter(
                    inner_variable_dimension_MAX__range=(height - error_margin, height + error_margin))

            # query products based on diameter
            if diameter:
                queryset = queryset.filter(diameter__range=(diameter - error_margin, diameter + error_margin))
                queryset_alt = queryset_alt.filter(diameter__range=(diameter - error_margin, diameter + error_margin))

            # merge querysets
            queryset_total = queryset | queryset_alt
            context['queryset'] = queryset_total
            context['model'] = Product

            def test():
                return "test"

            context['test_function'] = test

            # create table data

    return render(request, template_name, context)


class ProductCreate(PermissionRequiredMixin, CreateView):
    #template_name_suffix = '_other_suffix' default template is: model_name_form.html
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
