from django import forms
from .models import ProductType, Color, WallThickness, Product


class SearchProductForm(forms.Form):
    # product_type = forms.ModelChoiceField(queryset=ProductType.objects.all(), empty_label='All product types',
    #                                       required=False)
    # color = forms.ModelChoiceField(queryset=Color.objects.all(), empty_label='All colors', required=False)
    # wall_thickness = forms.ModelChoiceField(queryset=WallThickness.objects.all(), empty_label='All wall thicknesses',
    #                                         required=False)
    width = forms.IntegerField(required=False, label='Width in mm', widget=forms.NumberInput(attrs={
        'class': "form-control",
        'placeholder': "Breedte in mm",
    }))
    length = forms.IntegerField(required=False, label='Length in mm', widget=forms.NumberInput(attrs={
        'class': "form-control",
        'placeholder': "Lengte in mm",
    }))
    height = forms.IntegerField(required=False, label='Height in mm', widget=forms.NumberInput(attrs={
        'class': "form-control",
        'placeholder': "Hoogte in mm",
    }))
    diameter = forms.IntegerField(required=False, label='Diameter in mm')
    # error_margin = forms.IntegerField(initial=25, help_text='+/- dimension allowance')
    product_types = forms.ModelMultipleChoiceField(
        queryset=ProductType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        initial=[type for type in ProductType.objects.all()]
    )
    wall_thicknesses = forms.ModelMultipleChoiceField(
        queryset=WallThickness.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        initial=[wall_thickness for wall_thickness in WallThickness.objects.all()]
    )
    colors = forms.ModelMultipleChoiceField(
        queryset=Color.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        initial=[color for color in Color.objects.all()]

    )


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