from cities_light.models import City, Region, Country
from django.urls import reverse
from rest_framework.test import APITestCase
from users.models import CustomUser, Address, Seller
from rest_framework import status
from .models import Store, StoreType, ProductType, Product


class TestShop(APITestCase):

    def setUp(self):
        self.user_1 = CustomUser.objects.create()
        self.seller_1 = Seller.objects.create(user=self.user_1)
        self.type_1 = StoreType.objects.create()
        self.type_2 = StoreType.objects.create()
        self.country = Country.objects.create()
        self.province = Region.objects.create(country=self.country)
        self.city = City.objects.create(country=self.country, region=self.province)
        self.address_1 = Address.objects.create(user=self.user_1, city=self.city, province=self.province)
        self.address_2 = Address.objects.create(user=self.user_1, city=self.city, province=self.province)
        self.store_1 = Store.objects.create(owner=self.seller_1, address=self.address_1, type=self.type_1,
                                            status='confirmed', slug='af')
        self.store_2 = Store.objects.create(owner=self.seller_1, address=self.address_2, type=self.type_1)
        self.product_type = ProductType.objects.create(name='fg')
        self.product_1 = Product.objects.create(store=self.store_1, status='confirmed', quantity=10, price=3)
        self.product_2 = Product.objects.create(store=self.store_1, type=self.product_type, status='confirmed',
                                                quantity=2, price=8)
        self.product_3 = Product.objects.create(store=self.store_1, quantity=1, price=3)
        self.product_4 = Product.objects.create(store=self.store_1, status='confirmed', price=3)

    def test_type(self):
        url = reverse('store_types')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

    def test_store_list(self):
        url = reverse('stores')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_product_list(self):
        url = reverse('products', kwargs={'slug': self.store_1.slug})
        resp = self.client.get(url, format='json')
        products = []
        for i in resp.data:
            products.append(dict(i)['id'])
        self.assertIn(self.product_1.id, products)
        self.assertIn(self.product_2.id, products)
        self.assertNotIn(self.product_3.id, products)
        self.assertNotIn(self.product_4.id, products)

        url = reverse('products', kwargs={'slug': self.store_1.slug}) + '?type=f'
        resp = self.client.get(url)
        products = []
        for i in resp.data:
            products.append(dict(i)['id'])
        self.assertEqual(len(products), 1)
        self.assertNotIn(self.product_1.id, products)

    def test_cart_view(self):
        url = reverse('cart')
        self.client.force_authenticate(self.user_1)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_cart_item(self):
        url = reverse('cart_item')
        self.client.force_authenticate(self.user_1)
        data = {
            'product': self.product_1.id,
            'quantity': 11
        }
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        data = {
            'product': 700,
            'quantity': 1
        }
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        data = {
            'product': self.product_1.id,
            'quantity': 1
        }
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = {
            'product': self.product_1.id,
            'quantity': 2
        }
        resp = self.client.put(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = {
            'product': self.product_1.id,
        }
        resp = self.client.delete(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_payment(self):
        self.client.force_authenticate(self.user_1)
        data = {'addresses': '1 -'}
        url_1 = reverse('payment')
        resp = self.client.post(url_1, data)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        url_2 = reverse('cart')
        self.client.post(url_2)

        url = reverse('payment')
        resp = self.client.post(url_1, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
