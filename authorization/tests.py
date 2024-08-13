# authorization/tests.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class AuthTests(APITestCase):

    def setUp(self):
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'umar1671594@gmail.com'
        }

    def test_user_signup(self):
        response = self.client.post(self.signup_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')


    def test_user_login(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('csrf_token', response.data)

    def test_user_login_invalid_credentials(self):
        User.objects.create_user(**self.user_data)
        invalid_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
