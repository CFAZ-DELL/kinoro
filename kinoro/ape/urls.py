from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'ape'

urlpatterns = [
    path('report/', views.listreport, name='listreport'),
    path('report/<int:pk>/', views.report, name='report'),
    path('approve/<int:pk>/', views.approve, name='approve'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='ape/login.html'), name='login'),

    path('', views.dashboard, name='dashboard'),
]