import django_filters
from .models import Store, Product


class StoreListFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(field_name='type__title', lookup_expr='icontains')

    class Meta:
        model = Store
        fields = ['type']


class ProductListFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(field_name='type__name', lookup_expr='icontains')
    price_gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt')
    price_lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt')

    class Meta:
        model = Product
        fields = ('type', 'price_gt', 'price_lt')
