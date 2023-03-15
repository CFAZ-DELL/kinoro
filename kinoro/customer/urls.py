from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('', views.index, name='index'),
    path('tracking/', views.tracking, name='tracking'),
    path('product/', views.product , name='product'),
    path('cart/', views.cart , name='cart'),
]