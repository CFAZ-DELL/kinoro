from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('', views.index, name='index'),
    path('tracking/', views.tracking, name='tracking'),
    path('product/', views.product , name='product'),
    path('getcertificate/<int:pk>/', views.getCertificate, name='getcertificate'),
    path('addtocart/', views.addtocart , name='addtocart'),
    path('deletecart/<int:cart_quantity_id>/', views.deletecart , name='deletecart'),
    path('viewcart/', views.viewcart , name='viewcart'),
    path('certificate/<int:pk>/', views.certificate , name='certificate'),
    path('createbill/', views.createbill , name='createbill'),
    path('checkout/', views.checkout , name='checkout'),
]