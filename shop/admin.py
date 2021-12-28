from django.contrib import admin
from .models import Brand, Category, Product, ProductImage, Cart, CartItem, Favourite, Order, Store
# Register your models here.

admin.site.register(Brand)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Favourite)
admin.site.register(Order)
admin.site.register(Store)
# admin.site.register()
