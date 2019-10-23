from django.db import models
from django.urls import reverse


class Color(models.Model):
    color = models.CharField(max_length=120, verbose_name='Color', null=True)

    def __str__(self):
        return self.color or ""

    class Meta:
        ordering = ['color']

    def get_absolute_url(self):
        return reverse('color-detail', args=[str(self.id)])


class ProductType(models.Model):
    type = models.CharField(max_length=120, verbose_name='Product Type')

    def __str__(self):
        return self.type

    def get_absolute_url(self):
        return reverse('producttype-detail', args=[str(self.id)])

    class Meta:
        ordering = ['type']


class WallThickness(models.Model):
    wall_thickness = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.wall_thickness or ''

    def get_absolute_url(self):
        return reverse('wallthickness-detail', args=[str(self.id)])


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
    # TODO make prices to have more decimals, maybe
    inner_dim1 = models.PositiveIntegerField(blank=False, null=True, verbose_name='Inner width')
    inner_dim2 = models.PositiveIntegerField(blank=False, null=True, verbose_name='Inner length')
    inner_dim3 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Inner height')
    outer_dim1 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer width')
    outer_dim2 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer length')
    outer_dim3 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer height')
    inner_variable_dimension_MIN = models.PositiveIntegerField(blank=True, null=True,
                                                               verbose_name='Inner variable dimension min')
    inner_variable_dimension_MAX = models.PositiveIntegerField(blank=True, null=True,
                                                               verbose_name='Inner variable dimension max')
    outer_variable_dimension_MIN = models.PositiveIntegerField(blank=True, null=True,
                                                               verbose_name='Outer variable dimension min')
    outer_variable_dimension_MAX = models.PositiveIntegerField(blank=True, null=True,
                                                               verbose_name='Outer variable dimension max')
    diameter = models.PositiveIntegerField(blank=True, null=True, verbose_name='Diameter')
    bottles = models.PositiveIntegerField(blank=True, null=True, verbose_name='Number of bottles')
    standard_size = models.CharField(max_length=5, blank=True, null=True, verbose_name='Standard size')

    product_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=120, blank=True, default='', verbose_name='Product description')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, verbose_name='Color')
    wall_thickness = models.ForeignKey(WallThickness, on_delete=models.SET_NULL, null=True, verbose_name='Wall-thickness')
    in_stock = models.BooleanField(null=True, blank=True)

    url = models.URLField(max_length=120, blank=True, verbose_name='URL')

    price_ex_BTW = models.DecimalField(decimal_places=2, max_digits=1000, verbose_name="Price/box ex. BTW")
    price_incl_BTW = models.DecimalField(decimal_places=2, max_digits=1000, verbose_name="Price/box incl. BTW")
    minimum_purchase = models.PositiveIntegerField(blank=True, null=True, verbose_name='Bundle size')
    price_table = models.ManyToManyField('TierPrice')

    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return str(self.product_type) + ' ' + str(self.pk)

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('product-detail', args=[str(self.id)])

    def display_tierprices(self):
        """Create string for TierPrice's. This is required to display the tier-prices in Admin"""
        return ' | '.join(str(tierprice.tier) + ' á €' + str(tierprice.price) for tierprice in self.price_table.all())
    # This sets the header description
    display_tierprices.short_description = 'Staffelkorting'

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['product_type', 'inner_dim1']

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Product._meta.fields]

    def get_inner_dimensions(self):
        """Returns inner dimensions"""
        inner_dimension_list = ['inner_dim1', 'inner_dim2', 'inner_dim3', 'inner_variable_dimension_MIN',
                                'inner_variable_dimension_MAX', 'diameter']
        return self.get_field_value(inner_dimension_list)

    def get_outer_dimensions(self):
        """Returns outer dimensions"""
        outer_dimension_list = ['outer_dim1', 'outer_dim2', 'outer_dim3', 'outer_variable_dimension_MIN',
                                'outer_variable_dimension_MAX']
        return self.get_field_value(outer_dimension_list)

    def get_special_dimensions(self):
        """Returns bottles or standard size"""
        special_dimensions_list = ['bottles', 'standard_size']
        return self.get_field_value(special_dimensions_list)

    def get_overall_specifications(self):
        specification_list = ['company', 'description', 'color', 'wall_thickness']
        return self.get_field_value(specification_list)

    def get_field_value(self, dimension_list):
        """Helper method to return present dimensions. Yield a list of tuple (field_name, field_value)"""
        fields_values = []
        for dimension in dimension_list:
            if getattr(self, dimension) != None:
                fields_values.append((dimension, getattr(self, dimension)))

        if len(fields_values) == 0:
            return None
        return fields_values






class TierPrice(models.Model):
    tier = models.PositiveIntegerField(verbose_name='Tier')
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Price/box ex. BTW")

    #
    def __str__(self):
        return str(self.tier) + " : " + str(self.price)


class TestModel(models.Model):
    manyfield = models.ManyToManyField(Product)


model_list = [Color, ProductType, WallThickness, Product, Tag, TierPrice, TestModel]
