from django.contrib import admin
from .models import ExtendUser
from .models import ExtendUser, Address, Seller


admin.site.register(ExtendUser)
admin.site.register(Address)
admin.site.register(Seller)
# admin.site.register()
