from django.urls import path
from .views_api import *


urlpatterns = [
    path('store_type/', StoreTypeListView.as_view(), name='store_types'),
    path('stores/', StoreListView.as_view(), name='stores'),
    path('store/<slug:slug>/products/', ProductListView.as_view(), name='products'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart_item/', CartItemView.as_view(), name='cart_item'),
    path('payment/', Payment.as_view(), name='payment'),
    path('orders/', OrderListView.as_view(), name='orders'),
]
