from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Userdetails,Products,Category,Cart,BannerVedio,Useraddress,Order,Payment,Subcategory,Variants,Variantoptions,Productimages,Coupon

admin.site.register(Userdetails)
admin.site.register(Products)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Useraddress)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Subcategory)
admin.site.register(Variants)
admin.site.register(Variantoptions)
admin.site.register(Productimages)
admin.site.register(Coupon)
admin.site.register(BannerVedio)


