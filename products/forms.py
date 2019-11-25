from functools import reduce

from django import forms
from .models import ProductType, Color, WallThickness, Product, MainCategory
from django.db.models import Q
from products.product_categories import box_main_category_dict as box_cat
from products.product_categories import not_box_main_category_dict as not_box
import operator


class SearchProductForm(forms.Form):
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

    product_types = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        initial=None
    )
    wall_thicknesses = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        initial=None
    )
    colors = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        initial=None

    )

    def __init__(self, *args, **kwargs):
        super(SearchProductForm, self).__init__(*args, **kwargs)

        # Load queryset choices here so db calls are not made during migrations
        self.fields['product_types'].queryset = ProductType.objects.all()
        self.fields['product_types'].initial = [type for type in ProductType.objects.all()]
        self.fields['wall_thicknesses'].queryset = WallThickness.objects.all()
        self.fields['wall_thicknesses'].initial = [wall_thickness for wall_thickness in WallThickness.objects.all()]
        self.fields['colors'].queryset = Color.objects.all()
        self.fields['colors'].initial = [color for color in Color.objects.all()]


class SearchBoxForm(forms.Form):
    width = forms.IntegerField(required=False, label='Width in mm', min_value=0, widget=forms.NumberInput(attrs={
        'class': "form-control",
        'placeholder': "Breedte in mm",
    }))
    length = forms.IntegerField(required=False, label='Length in mm', min_value=0, widget=forms.NumberInput(attrs={
        'class': "form-control",
        'placeholder': "Lengte in mm",
    }))
    height = forms.IntegerField(required=False, label='Height in mm', min_value=0, widget=forms.NumberInput(attrs={
        'class': "form-control",
        'placeholder': "Hoogte in mm",
    }))

    product_type__main_category = forms.ChoiceField(
        widget=forms.Select,
        required=False,
        initial=None,
        )

    # wall_thicknesses = forms.ModelMultipleChoiceField(
    #     queryset=None,
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    #     initial=None
    # )
    # colors = forms.ModelMultipleChoiceField(
    #     queryset=None,
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    #     initial=None
    # )

    def __init__(self, *args, **kwargs):
        super(SearchBoxForm, self).__init__(*args, **kwargs)

        # Q objects & queryset for all box main_categories
        q_objects_main_categories = (Q(category=category) for category in box_cat.values())
        main_category_qset = MainCategory.objects.filter(reduce(operator.or_, q_objects_main_categories))

        # Category choices for form
        form_choices = [(category.id, category.category) for category in main_category_qset] + [('', 'Alle dozen')]

        # All sub categories:
        product_type_qset = ProductType.objects.filter(main_category__in=main_category_qset)

        # Q objects & queryset for all box type products
        q_objects_box = (Q(product_type=product_type) for product_type in
                         product_type_qset.values_list('id', flat=True))
        box_qset = Product.objects.filter(reduce(operator.or_, q_objects_box))

        # Create wallthickness and color queryset
        wall_thickness_qset = WallThickness.objects.filter(product__in=box_qset).distinct()
        color_qset = Color.objects.filter(product__in=box_qset).distinct()

        # Load queryset choices here so db calls are not made during migrations
        self.fields['product_type__main_category'].choices = form_choices
        # self.fields['main_categories'].initial = [category for category in main_category_qset]
        # self.fields['wall_thicknesses'].queryset = wall_thickness_qset
        # self.fields['wall_thicknesses'].initial = [wall_thickness for wall_thickness in wall_thickness_qset]
        # self.fields['colors'].queryset = color_qset
        # self.fields['colors'].initial = [color for color in color_qset]


class SearchTubeForm(forms.Form):
    diameter = forms.IntegerField(required=False, label='Height in mm', min_value=0, widget=forms.NumberInput(attrs={
        'class': "form-control",
        'placeholder': "Diameter in mm",
    }))

    length = forms.IntegerField(required=False, label='Length in mm', min_value=0, widget=forms.NumberInput(attrs={
        'class': "form-control",
        'placeholder': "Lengte in mm",
    }))

    product_type = forms.ChoiceField(
        widget=forms.Select,
        required=False,
        initial=None
    )
    # wall_thicknesses = forms.ModelMultipleChoiceField(
    #     queryset=None,
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    #     initial=None
    # )
    # colors = forms.ModelMultipleChoiceField(
    #     queryset=None,
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    #     initial=None
    # )

    def __init__(self, *args, **kwargs):
        super(SearchTubeForm, self).__init__(*args, **kwargs)

        main_category_qset = MainCategory.objects.get(id=14)
        category_qset = main_category_qset.producttype_set.all()

        # tubes_qset = Product.objects.filter(product_type__main_category__id=14)
        # wall_thickness_qset = WallThickness.objects.filter(product__in=tubes_qset).distinct()
        # color_qset = Color.objects.filter(product__in=tubes_qset).distinct()

        # populate initial values and queryset for selectboxes
        self.fields['product_type'].choices = [(category.id, category.type) for category in category_qset] + [('', 'Alle kokers')]
        # self.fields['categories'].initial = [category for category in category_qset]
        # self.fields['wall_thicknesses'].queryset = wall_thickness_qset
        # self.fields['wall_thicknesses'].initial = [wall_thickness for wall_thickness in wall_thickness_qset]
        # self.fields['colors'].queryset = color_qset
        # self.fields['colors'].initial = [color for color in color_qset]


class SearchEnvelopeBagForm(forms.Form):
    width = forms.IntegerField(required=False, label='Height in mm', widget=forms.NumberInput(attrs={
        'class': "form-control",
        'placeholder': "Breedte in mm",
    }))

    length = forms.IntegerField(required=False, label='Length in mm', widget=forms.NumberInput(attrs={
        'class': "form-control",
        'placeholder': "Lengte in mm",
    }))

    product_type = forms.ChoiceField(
        widget=forms.Select,
        required=False,
        initial=None
    )
    #
    # colors = forms.ModelMultipleChoiceField(
    #     queryset=None,
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    #     initial=None
    # )

    def __init__(self, *args, **kwargs):
        super(SearchEnvelopeBagForm, self).__init__(*args, **kwargs)

        main_category_qset = MainCategory.objects.get(pk=13)
        category_qset = main_category_qset.producttype_set.all()

        # products_qset = Product.objects.filter(product_type__main_category__category=13)
        # color_qset = Color.objects.filter(product__in=products_qset).distinct()

        # populate initial values and queryset for selectboxes
        self.fields['product_type'].choices = [(category.id, category.type) for category in category_qset] + [('', 'Alle zakken & enveloppen')]
        # self.fields['categories'].initial = [category for category in category_qset]
        # self.fields['colors'].queryset = color_qset
        # self.fields['colors'].initial = [color for color in color_qset]
