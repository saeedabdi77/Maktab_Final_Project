from .models import CustomUser
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.cache import cache


class UserApiTest(APITestCase):

    def setUp(self):
        self.payload = {
            "email": "a@abvc.com",
            "password": "aaaa8888888"
        }
        CustomUser.objects.create_user(**self.payload)

    def test_login(self):
        url = reverse('token_obtain_pair')
        resp = self.client.post(url, data=self.payload)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_register(self):
        url = reverse('user_register')
        data = {
            'email': 'a@aaa.com',
            'phone_number': '9887776644',
            'password': 'g3333333',
            'password2': 'g3333333',
            'first_name': 'a',
            'last_name': 'b',
            'gender': 'M'
        }
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(CustomUser.objects.get(email='a@aaa.com'))
        url_2 = reverse('profile')
        resp = self.client.get(url_2)
        self.assertEqual(dict(resp.data)['first_name'], 'a')

    def test_verify(self):
        url = reverse('user_register')
        data = {
            'email': 'a@aab.com',
            'phone_number': '9887776646',
            'password': 'g3333333',
            'password2': 'g3333333',
            'first_name': 'a',
            'last_name': 'b',
            'gender': 'M'
        }
        self.client.post(url, data=data)
        user = CustomUser.objects.get(email='a@aab.com')
        self.assertFalse(user.phone_number_verified)

        url_2 = reverse('otp')
        resp_2 = self.client.post(url_2, data={'phone': '9887776646'})
        self.assertEqual(resp_2.status_code, status.HTTP_401_UNAUTHORIZED)

        url_3 = reverse('send_verification_code')
        self.client.force_authenticate(user)
        resp_3 = self.client.post(url_3)
        self.assertEqual(resp_3.status_code, status.HTTP_200_OK)

        otp = cache.get(f'otp:9887776646')

        url_4 = reverse('enter_verification_code')
        self.client.post(url_4, data={'code': otp})
        self.assertTrue(user.phone_number_verified)

    def test_login_otp(self):
        url = reverse('user_register')
        data = {
            'email': 'a@aac.com',
            'phone_number': '9887776645',
            'password': 'g3333333',
            'password2': 'g3333333',
            'first_name': 'a',
            'last_name': 'b',
            'gender': 'M'
        }
        self.client.post(url, data=data)
        user = CustomUser.objects.get(email='a@aac.com')
        user.phone_number_verified = True
        user.save()

        url_2 = reverse('otp')
        resp = self.client.post(url_2, data={'phone': '9887776645'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        otp = cache.get(f'otp:9887776645')

        url_3 = reverse('token_obtain_pair')
        resp_2 = self.client.post(url_3, data={'email': '9887776645', 'password': otp})
        self.assertEqual(resp_2.status_code, status.HTTP_200_OK)
