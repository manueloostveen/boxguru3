from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

# Create your views here.
from products.models import Product, WallThickness, Color, ProductType

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
        'num_products':  num_products,
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
    def get_context_data(self, **kwargs):
        """Overriding method to add arbitrary data to the context"""

        # Call the base implementation first to get the context
        context = super(ProductListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

    paginate_by = 10

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
    def get_context_data(self, **kwargs):
        context = super(GenericListView, self).get_context_data(category_name=self.model._meta.verbose_name_plural.title(), **kwargs)
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

