from django.contrib import admin
from .models import Brand, Category, Product, ProductImage, Cart, CartItem, Favourite, Order, Store, ProductComment, \
    StoreType, ProductRate, ProductField, ProductType, ProductDetail
from django.utils.html import format_html


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'updated_at', 'total_price')
    list_filter = ['updated_at']
    search_fields = ['buyer__user__username']
    date_hierarchy = 'updated_at'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_image')
    date_hierarchy = 'created_at'
    list_filter = ('created_at', 'price', 'quantity', 'categories')
    search_fields = ('name', 'brand__name')
    list_per_page = 10
    fieldsets = (
        (None, {
            'fields': (('brand', 'name', 'price', 'quantity', 'type'), 'description', ('images', 'categories', 'comments'))
        }),

        ('slug', {
            'classes': ('collapse',),
            'fields': ['slug']
        }),
    )

    @admin.display(empty_value='-', description="show image")
    def show_image(self, obj):
        return format_html('<img src="{}" width=50 height=50/>', obj.get_default_image().url)


@admin.register(Favourite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__user__username']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('get_owner', 'get_updated_at', 'get_total', 'status')
    list_filter = ['status']

    def get_owner(self, obj):
        return obj.cart.buyer

    def get_updated_at(self, obj):
        return obj.cart.updated_at

    def get_total(self, obj):
        return obj.cart.total_price()


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ('publisher', 'text')
    search_fields = ['publisher__user__username']


@admin.action(description='Mark selected stores as confirmed')
def make_confirmed(modeladmin, request, queryset):
    queryset.update(status='confirmed')


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('get_seller', 'type', 'status')
    list_filter = ['status']
    list_editable = ['status']
    actions = [make_confirmed]

    def get_seller(self, obj):
        return obj.owner.user


admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(ProductImage)
admin.site.register(StoreType)
admin.site.register(ProductRate)
admin.site.register(ProductField)
admin.site.register(ProductDetail)
admin.site.register(ProductType)
# admin.site.register()
