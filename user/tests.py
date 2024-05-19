from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from user.models import CustomerUser

class UserCreateTest(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_admin(self):
        url = reverse('users-create')
        data = {
            "username": "admin",
            "password": "admin",
            "is_superuser": True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomerUser.objects.get(username=data['username']).username, "admin")
        self.assertEqual(CustomerUser.objects.get(username=data['username']).password, "admin")
        self.assertEqual(CustomerUser.objects.get(username=data['username']).is_superuser, True)

    def test_create_customer(self):
        url = reverse('users-create')
        data = {
            "username": "customer",
            "password": "customer",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomerUser.objects.get(username=data['username']).username, "customer")
        self.assertEqual(CustomerUser.objects.get(username=data['username']).password, "customer")
        self.assertEqual(CustomerUser.objects.get(username=data['username']).is_superuser, False)

    def test_create_customer_failed(self):
        self.test_create_customer()
        url = reverse('users-create')
        data = {
            "username": "customer",
            "password": "customer1",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_admin(self):
        self.test_create_admin()
        url = reverse('users-login')
        data = {
            "username": "admin",
            "password": "admin",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logged in successfully')
        self.assertEqual(CustomerUser.objects.get(username=data['username']).token, response.data['token'])

    def test_update_token(self):
        self.test_login_admin()
        admin = CustomerUser.objects.get(is_superuser=True)
        old_token = admin.token
        admin.generate_token(token=old_token)
        new_token = admin.token
        self.assertNotEqual(old_token, new_token)

    def test_login_customer(self):
        self.test_create_customer()
        url = reverse('users-login')
        data = {
            "username": "customer",
            "password": "customer",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logged in successfully')
        self.assertEqual(CustomerUser.objects.get(username=data['username']).token, response.data['token'])

    def test_login_customer_failed(self):
        self.test_create_customer()
        url = reverse('users-login')
        data = {
            "username": "customer1",
            "password": "customer",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_logout_customer(self):
        self.test_login_customer()
        url = reverse('users-logout')
        token = CustomerUser.objects.get().token
        response = self.client.post(url, headers={"Token": token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logged out successfully')
        self.assertEqual(CustomerUser.objects.get().token, None)