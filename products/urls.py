from django.urls import path, re_path
from . import views
from .models import Product, WallThickness, Color, ProductType


urlpatterns = [
    path('', views.index, name='index'),

    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),

    path('producttypes', views.GenericListView.as_view(model=ProductType), name='producttypes'),
    path('producttype/<int:pk>', views.GenericDetailView.as_view(
        model=ProductType
    ), name='producttype-detail'),

    path('colors/', views.GenericListView.as_view(
        model=Color
    ), name='colors'),

    path('colors/<int:pk>', views.GenericDetailView.as_view(
        model=Color
    ), name='color-detail'),

    path('wallthickness/', views.GenericListView.as_view(model=WallThickness), name='wallthickness'),

    path('wallthickness/<int:pk>',
         views.GenericDetailView.as_view(
                model=WallThickness),
                name='wallthickness-detail'),

    path('myproducts/', views.LikedProductsByUserView.as_view(), name='my-liked'),

    path('alllikedproducts/', views.AllLikedProductsByUsersView.as_view(), name='all-liked'),

]