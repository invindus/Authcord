from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from api.models import Author


# Create your tests here.

class SignUpTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.sign_up_user = {
            'username': 'testuser',
            'password': 'testuser123',
            'email': 'testuser@gmail.com'
        }
        self.signup_url = reverse('signup')

    def test_sign_up_user(self):
        response = self.client.post(self.signup_url, self.sign_up_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Author.objects.count(), 1)

    def test_signup_with_existing_username(self):
        self.client.post(self.signup_url, self.sign_up_user, format='json')
        response = self.client.post(self.signup_url, self.sign_up_user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertIn("A user with that username already exists.", str(response.data))


class LoginTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.sign_up_user = {
            'username': 'testuser',
            'password': 'testuser123',
            'email': 'testuser@gmail.com'
        }
        self.login_url = reverse('login')
        self.user = User.objects.create_user(**self.sign_up_user)
        self.author = Author.objects.create(user=self.user, is_approved=True)

    def test_login(self):
        response = self.client.post(self.login_url, {
            'username': self.sign_up_user['username'],
            'password': self.sign_up_user['password'],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', str(response.data))
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.data['token'], token.key)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': "userdeosnotexist",
            'password': "wrongpassword"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid Credentials', str(response.data))

    def test_login_unapproved_author(self):
        unapproved_author_user = User.objects.create_user(username='unapproveduser', password='test123456',
                                                          email='unapproveduser@gmail.com')
        Author.objects.create(user=unapproved_author_user, is_approved=False)

        # Attempt to log in
        response = self.client.post(self.login_url, {
            'username': 'unapproveduser',
            'password': 'test123456',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Author not approved by admin', str(response.data))
