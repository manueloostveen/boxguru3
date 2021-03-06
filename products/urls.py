from django.urls import path
from . import views
from .models import Product, WallThickness, Color, ProductType, MainCategory


urlpatterns = [
    path('', views.home, name='index'),
    path('like-unlike/<int:pk>/', views.like_unlike_box, name='like-unlike-product'),

    path('dozen-op-maat/', views.doos_op_maat, name='dozen-op-maat'),

    path('dozen/<str:hoofdcategorie>/', views.search_product, name='browse-maincategory'),

    path('dozen/<str:hoofdcategorie>/<str:subcategorie>', views.search_product, name='browse-subcategory'),

    path('mijn-bewaarde-dozen/', views.search_product, name='mijn-bewaarde-dozen'),

    path('products/', views.GenericListView.as_view(model=Product), name='products'),
    path('products/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),

    path('categories/product-types', views.GenericListView.as_view(model=ProductType), name='producttypes'),
    path('categories/product-type/<int:pk>', views.product_type_detail_view, name='producttype-detail'),

    path('dozen/', views.main_category_view, name='categories'),
    path('categories/<int:pk>/', views.main_category_detail_view, name='categories-detail'),

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

    path('like/<pk>/', views.like_product, name='like-product'),
    path('unlike/<pk>/', views.unlike_product, name='unlike-product'),

    path('zoek/', views.search_product, name='search-product'),
    path('zoek/<str:category_name>/', views.search_product, name='footer-search'),
    path('aanmelden/', views.signup, name='signup')
]

urlpatterns += [
    path('products/create/', views.ProductCreate.as_view(), name='product_create'),
    path('products/<int:pk>/update/', views.ProductUpdate.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', views.ProductDelete.as_view(), name='product_delete'),
]

urlpatterns += [
    path('bootstrap/', views.bootstrap, name='bootstrap')
]