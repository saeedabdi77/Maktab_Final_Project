from .models import CustomUser
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


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
