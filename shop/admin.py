from django.contrib import admin
from .models import Brand, Category, Product, ProductImage, Cart, CartItem, Favourite, Order, Store, ProductComment
from django.utils.html import format_html


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity')


class CartAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'updated_at', 'total_price')
    list_filter = ['updated_at']
    search_fields = ['buyer__user__username']
    date_hierarchy = 'updated_at'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_image')
    date_hierarchy = 'created_at'
    list_filter = ('created_at', 'price', 'quantity', 'categories')
    search_fields = ('name', 'brand__name')
    list_per_page = 10
    fieldsets = (
        (None, {
            'fields': (('brand', 'name', 'price', 'quantity'), 'description', ('images', 'categories', 'comments'))
        }),

        ('slug', {
            'classes': ('collapse',),
            'fields': ['slug']
        }),
    )

    @admin.display(empty_value='-', description="show image")
    def show_image(self, obj):
        return format_html('<img src="{}" width=50 height=50/>', obj.get_main_image().url)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__user__username']


# class CommentInline(admin.TabularInline):
#     model = Comment


class OrderAdmin(admin.ModelAdmin):
    list_display = ('cart__buyer', 'cart__updated_at', 'cart__total_price', 'status')
    list_filter = ['cart__updated_at']
    search_fields = ['cart__buyer__user__username']
    date_hierarchy = 'cart__updated_at'

    # inlines = [
    #     CommentInline,
    # ]


class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ('publisher', 'text')
    search_fields = ['publisher__user__username']


admin.site.register(Brand)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Favourite, FavoriteAdmin)
admin.site.register(ProductComment, ProductCommentAdmin)

admin.site.register(Order)
admin.site.register(Store)
# admin.site.register()
