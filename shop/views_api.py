from rest_framework import generics, mixins
from .serializers import StoreTypeSerializer, StoreSerializer, ProductSerializer, CartItemSerializer, \
    ActiveCartSerializer, OrderSerializer, DeleteCartItemSerializer, OrderAddressSerializer
from .models import StoreType, Store, Product, Cart, CartItem, Order
from .filters import StoreListFilter, ProductListFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FormParser, MultiPartParser
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ObjectDoesNotExist
from cities_light.models import City, Region
from users.models import Address


class StoreTypeListView(generics.GenericAPIView, mixins.ListModelMixin):
    queryset = StoreType.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StoreTypeSerializer


class StoreListView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Store.objects.filter(status='confirmed').all()
    filterset_class = StoreListFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StoreSerializer


class ProductListView(mixins.ListModelMixin, generics.GenericAPIView):
    filterset_class = ProductListFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Product.objects.filter(store__slug=slug).filter(status='confirmed').filter(quantity__gt=0).all()


class CartView(mixins.CreateModelMixin, generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = Cart.objects.filter(buyer=self.request.user).get(order=None)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response(data={'message': 'NO active cart'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        CartItem.objects.filter(cart__buyer=request.user).filter(cart__order=None).delete()
        Cart.objects.filter(buyer=request.user).filter(order=None).delete()
        cart = Cart.objects.create(buyer=request.user)
        return Response({'id': cart.pk}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            for item in CartItem.objects.filter(cart__buyer=request.user).filter(cart__order=None):
                self.perform_destroy(item)
            instance = Cart.objects.filter(buyer=self.request.user).get(order=None)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(data={'message': 'NO active cart'}, status=status.HTTP_404_NOT_FOUND)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ActiveCartSerializer


class CartItemView(mixins.CreateModelMixin, generics.GenericAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @swagger_auto_schema(request_body=DeleteCartItemSerializer)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        try:
            if not Cart.objects.filter(order=None).filter(buyer=request.user).exists():
                Cart.objects.create(buyer=request.user)
            if not Product.objects.filter(id=int(request.data['product'])).exists():
                raise ObjectDoesNotExist
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except ValueError:
            return Response(data={'message': 'Invalid amount'}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            return Response(data={'message': 'Product not found!'}, status=status.HTTP_404_NOT_FOUND)
        except TypeError:
            return Response(data={'message': 'You can not have products from different stores in one cart'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = CartItem.objects.filter(cart__order=None).filter(cart__buyer=request.user).get(
                product=request.data['product'])
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            if int(request.data['quantity']) < 1:
                instance.delete()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            Response(data={'message': 'Product not found!'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        product = request.data['product']
        try:
            instance = CartItem.objects.filter(cart__order=None).filter(cart__buyer=request.user).get(
                product=Product.objects.get(id=product))
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CartItemSerializer
        elif self.request.method == 'PUT':
            return CartItemSerializer
        elif self.request.method == 'DELETE':
            return DeleteCartItemSerializer


class Payment(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderAddressSerializer
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request):
        try:
            cart = Cart.objects.filter(order=None).get(buyer=request.user)
            if 'addresses' in request.data:
                number = request.data['addresses'].split(' -')[0]
                address = Address.objects.filter(user=request.user)[int(number) - 1]
                Order.objects.create(cart=cart, status='paid', address=address)
            else:
                address = Address.objects.create(user=request.user,
                                                 province=Region.objects.get(name=request.data['province']),
                                                 city=City.objects.get(name=request.data['city']),
                                                 zip_code=request.data['zip_code'],
                                                 address_description=request.data['address_description'])
                Order.objects.create(cart=cart, status='paid', address=address)
            return Response(data={'message': 'payment successful!'}, status=status.HTTP_201_CREATED)
        except MultiValueDictKeyError:
            return Response(data={'message': 'Invalid address!'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except ObjectDoesNotExist:
            return Response(data={'message': 'no active cart'}, status=status.HTTP_404_NOT_FOUND)


class OrderListView(generics.GenericAPIView, mixins.ListModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = Order.objects.filter(cart__buyer=self.request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
