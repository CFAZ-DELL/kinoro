from django.contrib import admin
from .models import Package, CartQuantity, Cart, Address, Bill, Order, OrderQuantity, Tracking, Certificate, Report

# Register your models here.
admin.site.register(Package)
admin.site.register(CartQuantity)
admin.site.register(Cart)
admin.site.register(Address)
admin.site.register(Bill)
admin.site.register(Order)
admin.site.register(OrderQuantity)
admin.site.register(Tracking)
admin.site.register(Certificate)
admin.site.register(Report)
