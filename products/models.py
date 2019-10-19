from django.db import models
from django.urls import reverse



class Color(models.Model):
    color = models.CharField(max_length=120, verbose_name='Color', null=True)

    def __str__(self):
        return self.color or ""

    class Meta:
        ordering = ['color']

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

class Tag(models.Model):
    tag = models.CharField(max_length=120, verbose_name='Tag')

    def __str__(self):
        return self.tag

    class Meta:
        ordering = ['tag']


class Product(models.Model):
    inner_dim1 = models.PositiveIntegerField(blank=False, null=True, verbose_name='Inner width (mm)')
    inner_dim2 = models.PositiveIntegerField(blank=False, null=True, verbose_name='Inner length (mm)')
    inner_dim3 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Inner height (mm)')
    outer_dim1 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer width (mm)')
    outer_dim2 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer length (mm)')
    outer_dim3 = models.PositiveIntegerField(blank=True, null=True, verbose_name='Outer height (mm)')
    inner_variable_dimension_MIN = models.PositiveIntegerField(blank=True, null=True,
                                                    verbose_name='Inner variable dimension min (mm)')
    inner_variable_dimension_MAX = models.PositiveIntegerField(blank=True, null=True,
                                                    verbose_name='Inner variable dimension max (mm)')
    outer_variable_dimension_MIN = models.PositiveIntegerField(blank=True, null=True,
                                                    verbose_name='Outer variable dimension min (mm)')
    outer_variable_dimension_MAX = models.PositiveIntegerField(blank=True, null=True,
                                                    verbose_name='Outer variable dimension max (mm)')
    diameter = models.PositiveIntegerField(blank=True, null=True, verbose_name='Diameter (mm)')
    bottles = models.PositiveIntegerField(blank=True, null=True, verbose_name='Number of bottles')
    standard_size = models.CharField(max_length=5, blank=True, null=True, verbose_name='Standard size')
    description = models.CharField(max_length=120, blank=True, default='', verbose_name='Product description')
    in_stock = models.BooleanField(null=True, blank=True)
    minimum_purchase = models.PositiveIntegerField(blank=True, null=True, verbose_name='Bundle size')
    url = models.URLField(max_length=120, blank=True, verbose_name='URL')
    company = models.CharField(max_length=120, verbose_name='Company')
    price_ex_BTW = models.DecimalField(decimal_places=2, max_digits=1000, verbose_name="Price/box ex. BTW")
    price_incl_BTW = models.DecimalField(decimal_places=2, max_digits=1000, verbose_name="Price/box incl. BTW")

    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    product_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True)
    wall_thickness = models.ForeignKey(WallThickness, on_delete=models.SET_NULL, null=True)
    price_table = models.ManyToManyField('TierPrice')
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return "product " + str(self.product_type) + '' + str(self.pk)

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('product-detail', args=[str(self.id)])

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['product_type', 'inner_dim1']


class TierPrice(models.Model):
    tier = models.PositiveIntegerField(verbose_name='Tier')
    price = models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Price/box ex. BTW")
    #
    def __str__(self):
        return str(self.tier) + " : " + str(self.price)



class TestModel(models.Model):
    manyfield = models.ManyToManyField(Product)

model_list = [Color, ProductType, WallThickness, Product, Tag, TierPrice, TestModel]