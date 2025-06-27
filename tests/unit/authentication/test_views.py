from django.contrib.auth import get_user_model
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()
fake = Faker()


class AuthenticationViewsTests(APITestCase):
    """Test authentication views"""

    def setUp(self):
        """Set up test data"""

        self.login_data = {
            'email': fake.email(),
            'password': fake.password(length=8)
        }
        self.user = User.objects.create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=self.login_data['email'],
            password=self.login_data['password']
        )
        self.login_url = reverse('login')
        self.refresh_url = reverse('refresh')
        self.verify_url = reverse('verify')

    def test_LoginViewSet_with_valid_credentials(self):
        """Test login API with valid credentials"""

        response = self.client.post(self.login_url, self.login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_LoginViewSet_with_inactive_user(self):
        """Test login API with an inactive user"""

        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.login_url, self.login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('no_active_account', response.data['detail'].code)

    def test_TokenVerifyViewSet_with_valid_token(self):
        """Test token verify API with valid access and refresh token"""

        response = self.client.post(self.login_url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        access_token = response.data['access']
        refresh_token = response.data['refresh']

        # Verify a valid access token
        response = self.client.post(self.verify_url, {"token": access_token}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify a valid refresh token
        response = self.client.post(self.verify_url, {"token": refresh_token}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_TokenVerifyViewSet_with_invalid_token(self):
        """Test token verify API with invalid token"""

        response = self.client.post(self.login_url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify a valid access token
        response = self.client.post(self.verify_url, {"token": "invalid_access_token"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_LoginViewSet_with_invalid_credentials(self):
        """Test login API with invalid credentials"""

        self.login_data['password'] = 'wrongpassword'
        response = self.client.post(self.login_url, self.login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_LoginViewSet_with_missing_credentials(self):
        """Test login API with missing credentials"""

        # Missing email
        response = self.client.post(self.login_url,
                                    {'password': self.login_data['password']},
                                    format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing password
        response = self.client.post(self.login_url,
                                    {'email': self.login_data['email']},
                                    format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_RefreshViewSet_with_valid_refresh_token(self):
        """Test refresh API with a valid refresh token"""

        response = self.client.post(self.login_url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token = response.data['refresh']

        response = self.client.post(self.refresh_url, {"refresh": refresh_token}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_RefreshViewSet_with_invalid_refresh_token(self):
        """Test refresh API with an invalid refresh token"""

        response = self.client.post(self.login_url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(self.refresh_url, {"refresh": "invalid refresh token"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserAccountViewsTests(APITestCase):
    """Test user account views"""

    def setUp(self):
        """Set up test data"""

        self.user_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "password": fake.password(length=8)
        }

        self.create_user_url = reverse('user-list')
        self.get_user_url = reverse('user-me')
        self.login_url = reverse('login')
        self.verify_url = reverse('verify')

    def test_create_user_api_with_valid_data(self):
        """Test create user API with valid data"""

        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('email', response.data)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)

        new_user = User.objects.get(pk=response.data['id'])
        self.assertEqual(new_user.email, self.user_data['email'])
        self.assertEqual(new_user.username, self.user_data['email'])
        self.assertEqual(new_user.first_name, self.user_data['first_name'])
        self.assertEqual(new_user.last_name, self.user_data['last_name'])

    def test_create_user_api_with_missing_required_fields(self):
        """Test create user API with missing required fields"""

        # Missing email
        temp = self.user_data.pop('email')
        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user_data['email'] = temp

        # Missing first_name
        temp = self.user_data.pop('first_name')
        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user_data['first_name'] = temp

        # Missing last_name
        temp = self.user_data.pop('last_name')
        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user_data['last_name'] = temp

        # Missing password
        temp = self.user_data.pop('password')
        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user_data['password'] = temp

    def test_create_user_api_with_invalid_data(self):
        """Test create user API with invalid data"""

        # Invalid email
        temp = self.user_data.get('email')
        self.user_data['email'] = 'invalid_email'
        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user_data['email'] = temp

        # Invalid first_name
        temp = self.user_data.get('first_name')
        self.user_data['first_name'] = ''
        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user_data['first_name'] = temp

        # Invalid last_name
        temp = self.user_data.get('last_name')
        self.user_data['last_name'] = ''
        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user_data['last_name'] = temp

    def test_create_user_api_with_invalid_password(self):
        """Test create user API with invalid passwords"""

        # User Attribute Similarity Validator
        # With email
        self.user_data['password'] = self.user_data['email']
        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertIn('password_too_similar', [errors.code for errors in response.data['password']])

        # With first_name
        self.user_data['password'] = self.user_data['first_name']
        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertIn('password_too_similar', [errors.code for errors in response.data['password']])

        # With last_name
        self.user_data['password'] = self.user_data['last_name']
        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertIn('password_too_similar', [errors.code for errors in response.data['password']])

    def test_create_user_api_with_duplicate_email(self):
        """Test create user API with duplicate email"""

        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.create_user_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
