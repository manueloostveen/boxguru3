from django.contrib import admin
from .models import Color, ProductType, WallThickness, Product, Tag, TierPrice, Company, MainCategory

admin.site.register(Tag)
admin.site.register(TierPrice)
admin.site.register(Company)
admin.site.register(MainCategory)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('company', 'price_ex_BTW', 'display_users', 'display_tierprices')
    list_filter = ('company', 'product_type', 'wall_thickness', 'color', 'tags')
    ## Use 'fields = ' to show only specific fields, change order, show them horizontally
    # fields = [('inner_dim1', 'inner_dim2', 'inner_dim3'),
    #           ('inner_variable_dim_MIN', 'inner_variable_dim_MAX')]

    fieldsets = (
        ('Inner dimensions', {
            'fields': (('inner_dim1', 'inner_dim2', 'inner_dim3'), ('inner_variable_dimension_MIN', 'inner_variable_dimension_MAX'), 'diameter', 'bottles', 'standard_size')
        }),
        ('Outer dimensions', {'fields': (('outer_dim1', 'outer_dim2', 'outer_dim3'), ('outer_variable_dimension_MIN', 'outer_variable_dimension_MAX'))
        }),
        ('Price', {
            'fields': (('price_ex_BTW', 'price_incl_BTW'), 'minimum_purchase', 'price_table', 'lowest_price')
        }),
        ('Other specifications', {
            'fields': ('company', 'description', 'product_type', 'color', 'wall_thickness', 'url')
        }),
        ('Liked by', {
            'fields': ['users']
        })
    )


class ProductsInline(admin.TabularInline):
    """An inline class can be used to edit associated records at the same time"""
    model = Product
    extra = 0 # extra can be used to have blank entry fields at the bottom of the list for objects
    fieldsets = (
        ('Specifications', {
            'fields': ('company', 'product_type', 'color', 'wall_thickness', 'url')
        }),
        ('Price', {
            'fields': ('price_ex_BTW', 'price_table')
        })
    )
    readonly_fields = ('company', 'product_type', 'color', 'wall_thickness', 'url', 'price_ex_BTW', 'price_table')

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = [('color')]
    inlines = [ProductsInline]

@admin.register(WallThickness)
class WallThicknessAdmin(admin.ModelAdmin):
    inlines = [ProductsInline]

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    # inlines = [ProductsInline]
    pass
