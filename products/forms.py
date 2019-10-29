from django import forms
from .models import ProductType, Color, WallThickness, Product


class SearchProductForm(forms.Form):
    product_type = forms.ModelChoiceField(queryset=ProductType.objects.all(), empty_label='All product types',
                                          required=False)
    color = forms.ModelChoiceField(queryset=Color.objects.all(), empty_label='All colors', required=False)
    wall_thickness = forms.ModelChoiceField(queryset=WallThickness.objects.all(), empty_label='All wall thicknesses',
                                            required=False)
    width = forms.IntegerField(required=False, label='Width in mm')
    length = forms.IntegerField(required=False, label='Length in mm')
    height = forms.IntegerField(required=False, label='Height in mm')
    diameter = forms.IntegerField(required=False, label='Diameter in mm')
    error_margin = forms.IntegerField(initial=25, help_text='+/- dimension allowance')

class SearchProductModelForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_type',
            'color',
            'wall_thickness',
            'inner_dim1',
            'inner_dim2',
            'inner_dim3',
            'diameter',
        ]