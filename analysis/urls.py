from django.urls import path
from . import views

urlpatterns = [
    path('ajax/collect_reffered_link/', views.save_clicked_link, name='save-click')
]