from django.db import models
from django.urls import reverse
# from django.contrib.auth.models import User
from users.models import CustomUser


class MainCategory(models.Model):
    id = models.BigIntegerField(primary_key=True)
    category = models.CharField(max_length=120, verbose_name='Hoofdcategorie', null=True)
    category_id = models.IntegerField(blank=True,verbose_name='Category id')
    category_url = models.CharField(max_length=120, verbose_name='URL-naam', null=True)

    def __str__(self):
        return self.category

    def get_absolute_url(self):
        return reverse('categories-detail', args=[str(self.id)])

    class Meta:
        ordering = ['category']
        verbose_name = 'Hoofdcategorie'
        verbose_name_plural = 'Hoofdcategoriën'


class Color(models.Model):
    color = models.CharField(max_length=120, verbose_name='Color', null=True)

    def __str__(self):
        return self.color or ""

    class Meta:
        ordering = ['color']
        verbose_name = 'Color'

    def get_absolute_url(self):
        return reverse('color-detail', args=[str(self.id)])


class ProductType(models.Model):
    id = models.BigIntegerField(primary_key=True)

    type = models.CharField(max_length=120, verbose_name='Product Type')
    type_singular = models.CharField(max_length=120, verbose_name='Product Type Singular', blank=True, null=True)
    main_category = models.ForeignKey(MainCategory, on_delete=models.SET_NULL, blank=True, null=True)
    product_type_id = models.IntegerField(blank=True)

    def __str__(self):
        return self.type

    def get_absolute_url(self):
        return reverse('producttype-detail', args=[str(self.id)])

    class Meta:
        ordering = ['type']
        verbose_name = 'Product type'


class WallThickness(models.Model):
    wall_thickness = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.wall_thickness or ''

    def get_absolute_url(self):
        return reverse('wallthickness-detail', args=[str(self.id)])

    class Meta:
        verbose_name = 'Wallthickness'
        verbose_name_plural = "Wallthicknesses"


class Tag(models.Model):
    tag = models.CharField(max_length=120, verbose_name='Tag')

    def __str__(self):
        return self.tag

    class Meta:
        ordering = ['tag']


class Company(models.Model):
    company = models.CharField(max_length=120, verbose_name='Company')

    def __str__(self):
        return self.company

    class Meta:
        ordering = ['company']


class Product(models.Model):
    inner_dim1 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Inner width')
    inner_dim2 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Inner length')
    inner_dim3 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Inner height')
    outer_dim1 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer width')
    outer_dim2 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer length')
    outer_dim3 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer height')
    volume = models.DecimalField(blank=True, null=True, decimal_places=4, max_digits=10, verbose_name='Volume')

    inner_variable_dimension_MIN = models.PositiveIntegerField(blank=True, null=True,
                                                               verbose_name='Inner variable dimension min')
    inner_variable_dimension_MAX = models.PositiveIntegerField(blank=True, null=True,
                                                               verbose_name='Inner variable dimension max')
    outer_variable_dimension_MIN = models.PositiveIntegerField(blank=True, null=True,
                                                               verbose_name='Outer variable dimension min')
    outer_variable_dimension_MAX = models.PositiveIntegerField(blank=True, null=True,
                                                               verbose_name='Outer variable dimension max')
    variable_height = models.BooleanField(blank=True, null=True)

    height_sorter = models.PositiveIntegerField(blank=True, null=True, verbose_name='Sortable height')

    diameter = models.PositiveIntegerField(blank=True, null=True, verbose_name='Diameter')
    bottles = models.PositiveIntegerField(blank=True, null=True, verbose_name='Number of bottles')
    standard_size = models.CharField(max_length=5, blank=True, null=True, verbose_name='Standard size')

    product_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Product type')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=120, blank=True, default='', verbose_name='Product description')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, verbose_name='Color')
    wall_thickness = models.ForeignKey(WallThickness, on_delete=models.SET_NULL, null=True,
                                       verbose_name='Wall-thickness')
    in_stock = models.BooleanField(null=True, blank=True)

    url = models.URLField(max_length=120, blank=True, verbose_name='URL')

    price_ex_BTW = models.DecimalField(decimal_places=2, max_digits=1000, verbose_name="Price/box ex. BTW")
    price_incl_BTW = models.DecimalField(decimal_places=2, max_digits=1000, verbose_name="Price/box incl. BTW")
    minimum_purchase = models.PositiveIntegerField(blank=True, null=True, verbose_name='Bundle size')
    price_table = models.ManyToManyField('TierPrice')
    lowest_price = models.DecimalField(decimal_places=2, max_digits=1000, null=True, blank=True, verbose_name="Lowest price/box ex. BTW")

    tags = models.ManyToManyField(Tag)

    users = models.ManyToManyField(CustomUser, verbose_name='Liked by', blank=True)

    product_image = models.CharField(max_length=200, blank=True, null=True)


    inner_dimensions = ['inner_dim1', 'inner_dim2', 'inner_dim3', 'inner_variable_dimension_MIN',
                        'inner_variable_dimension_MAX', 'diameter']
    outer_dimensions = ['outer_dim1', 'outer_dim2', 'outer_dim3', 'outer_variable_dimension_MIN',
                        'outer_variable_dimension_MAX']
    special_dimensions = ['bottles', 'standard_size']
    specifications = ['company', 'description', 'color', 'wall_thickness']
    price_fields = ['price_ex_BTW', 'price_incl_BTW']

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['inner_dim1']
        permissions = (
            ('can_see_all_liked_products', 'Get list of liked products'),
            ('create_update_delete', 'Create/update/delete products'),
        )

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('product-detail', args=[str(self.id)])

    def display_tierprices(self):
        """Create string for TierPrice's. This is required to display the tier-prices in Admin"""
        return ' | '.join(str(tierprice.tier) + ' á €' + str(tierprice.price) for tierprice in self.price_table.all())

    def display_product_types(self):
        return self.product_type
        # return ''.join(str(product_type.type) for product_type in self.product_type.all() if product_type.pk != 115)

    def display_product_type_singular(self):
        return str(self.product_type.product_type_id)
        # return ''.join(str(product_type.type_singular) for product_type in self.product_type.all() if product_type.pk != 115)

    def popover_tierprices(self):
        return [str(tierprice.tier) + ' á €' + str(tierprice.price) for tierprice in self.price_table.order_by('-price').all()]

    def popover_tierprices_dict(self):
        return {str(tierprice.tier): str(tierprice.price) for tierprice in self.price_table.order_by('-price').all()}

    def display_users(self):
        """Create string for Users that liked this product."""
        return ', '.join(str(user) for user in self.users.all())

    def get_all_table_fields(self):
        return self.inner_dimensions + self.special_dimensions + self.price_fields + self.specifications

    def get_dimension_fields(self):
        return self.inner_dimensions

    def get_remaining_table_fields(self):
        return self.special_dimensions + self.price_fields + self.specifications

    def get_product_image(self):

        if self.product_image != None:
            return self.product_image
        # else:
        #     return self.display_product_type_singular()
        else:
            return 'standaard_dozen/' + 'standaard_dozen_afbeeldingen_' + self.display_product_type_singular() + '.jpg'

    # This sets the header descriptions in admin
    display_tierprices.short_description = 'Staffelkorting'
    display_users.short_description = 'Liked by'

    def get_all_field_names(self):
        return [(field.name, field.value_to_string(self)) for field in Product._meta.fields]

    def get_inner_dimensions(self):
        """Returns inner dimensions"""
        return self.get_field_value(self.inner_dimensions)

    def get_outer_dimensions(self):
        """Returns outer dimensions"""
        return self.get_field_value(self.outer_dimensions)

    def get_special_dimensions(self):
        """Returns bottles or standard size"""
        return self.get_field_value(self.special_dimensions)

    def get_overall_specifications(self):
        """Returns overall specifications"""
        return self.get_field_value(self.specifications)

    def get_field_value(self, dimension_list):
        """Helper method to return present dimensions. Yield a list of tuple (field_name, field_value)"""
        fields_values = []
        for dimension in dimension_list:
            if getattr(self, dimension) != None:
                fields_values.append((dimension, getattr(self, dimension)))

        if len(fields_values) == 0:
            return None
        return fields_values

    def __str__(self):
        description = str(self.product_type) + ' |'
        inner_dimensions = self.get_inner_dimensions()
        if inner_dimensions != None:
            for field, value in inner_dimensions[:-1]:
                description += f" {value} x "
            description += f'{inner_dimensions[-1][1]} mm'
        return description


class TierPrice(models.Model):
    tier = models.PositiveIntegerField(verbose_name='Tier')
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Price/box ex. BTW")

    #
    def __str__(self):
        return str(self.tier) + " : " + str(self.price)


class TestModel(models.Model):
    manyfield = models.ManyToManyField(Product)


model_list = [Color, ProductType, WallThickness, Product, Tag, TierPrice, TestModel]
