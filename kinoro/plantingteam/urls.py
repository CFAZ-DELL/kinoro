from django.urls import path
from . import views

app_name = 'plantingteam'

urlpatterns = [
    path('generate/', views.generate, name='generate'),
    path('order/', views.orderlist, name='orderlist'),
    path('order/<int:pk>/', views.order, name='order'),
    path('orderlatlong/<int:pk>/', views.orderlatlong, name='orderlatlong'),
    path('', views.dashboard, name='dashboard')
]