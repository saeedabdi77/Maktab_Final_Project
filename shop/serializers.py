from rest_framework import serializers
from .models import StoreType, Store, Product, ProductType, Cart, CartItem, Order
from users.models import Address, CustomUser
from cities_light.models import Region, City
from django.core.exceptions import ObjectDoesNotExist


class StoreTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreType
        fields = ['title']


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['name']


class AddressSerializer(serializers.ModelSerializer):
    province = ProvinceSerializer()

    class Meta:
        model = Address
        fields = ['province']


class StoreSerializer(serializers.ModelSerializer):
    type = StoreTypeSerializer()
    address = AddressSerializer()

    class Meta:
        model = Store
        fields = ['name', 'type', 'address', 'image']


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ['name']


class ProductSerializer(serializers.ModelSerializer):
    type = ProductTypeSerializer()
    store = StoreSerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'type', 'store', 'price', 'quantity']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('product', 'quantity')

    def create(self, validated_data):
        user = self.context['request'].user
        cart_item = CartItem(
            cart=Cart.objects.filter(order=None).get(buyer=user),
            product=validated_data['product'],
            quantity=validated_data['quantity']
        )
        cart_item.save()
        return cart_item


class ActiveCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('product', 'quantity')


class ActiveCartSerializer(serializers.ModelSerializer):
    cart_items = ActiveCartItemSerializer(source='cartitem_set', many=True)

    class Meta:
        model = Cart
        fields = ['cart_items', 'total_price']


class CartOrderSerializer(serializers.ModelSerializer):
    cart_items = ActiveCartItemSerializer(source='cartitem_set', many=True)

    class Meta:
        model = Cart
        fields = ['cart_items', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    cart = CartOrderSerializer()

    class Meta:
        model = Order
        fields = ['cart', 'status']


class DeleteCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product']


class OrderAddressSerializer(serializers.Serializer):
    province = serializers.ChoiceField(choices=[(item.name, item) for item in Region.objects.all()], required=False)
    city = serializers.ChoiceField(choices=[(item.name, item) for item in City.objects.all()], required=False)
    zip_code = serializers.CharField(max_length=15, required=False)
    address_description = serializers.CharField(max_length=1000, required=False)

    def __init__(self, *args, **kwargs):
        super(OrderAddressSerializer, self).__init__(*args, **kwargs)
        try:
            self.fields['addresses'] = serializers.ChoiceField(choices=[
                (
                    f'{index + 1} - {item.province.name} - {item.city.name} - {item.address_description} - {item.zip_code} ',
                    item) for index, item in enumerate(Address.objects.filter(user=self.context['request'].user))],
                required=False)
        except:
            pass
