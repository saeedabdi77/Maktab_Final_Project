from django.urls import path, include
from .views import *

urlpatterns = [
    path('home/', Home.as_view(), name='shop-home'),
    path('my-stores/', MyStores.as_view(), name='shop-my-stores'),
    path('add-store/', AddStore.as_view(), name='add-store'),
    path('store-detail/<int:pk>/', StoreDetail.as_view(), name='store-detail'),
    path('delete-store/<int:pk>/', DeleteStore.as_view(), name='delete-store'),
    path('edit-store/<int:pk>/', EditStore.as_view(), name='edit-store'),
    path('add-product/<int:pk>/', AddProduct.as_view(), name='add-product'),
    path('edit-product/<int:pk>/', EditProduct.as_view(), name='edit-product'),
    path('product-detail/<slug:slug>/', GetProductFields.as_view(), name='product-detail'),
    path('default-product-image/<int:pk>/', SetDefaultImage.as_view(), name='default-product-image'),
    path('set-product-fields/<int:pk>/', AddProductFields.as_view(), name='set-product-fields'),
    path('store-orders/<int:pk>/', StoreOrder.as_view(), name='store-orders'),
    path('store-customers/<int:pk>/', StoreCustomers.as_view(), name='store-customers'),
    path('store-report/<int:pk>/', StoreReport.as_view(), name='store-report'),
]
