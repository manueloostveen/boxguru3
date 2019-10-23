from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),
    path('producttypes', views.ProductTypeListView.as_view(), name='producttypes'),
    path('producttype/<int:pk>', views.ProductTypeDetailView.as_view(), name='producttype-detail'),
    path('colors/', views.ColorListView.as_view(), name='colors'),
    path('colors/<int:pk>', views.ColorDetailView.as_view(), name='color-detail'),
    path('wallthickness/', views.WallThicknessListView.as_view(), name='wallthickness'),
    path('wallthickness/<int:pk>', views.WallThicknessDetailView.as_view(), name='wallthickness-detail')

]