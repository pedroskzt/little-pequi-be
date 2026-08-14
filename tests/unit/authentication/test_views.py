from django.contrib.auth import get_user_model
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

User = get_user_model()
fake = Faker()


class AuthenticationViewsTests(APITestCase):
    """Test authentication views"""

    def setUp(self):
        """Set up test data"""

        self.signIn_data = {
            'email': fake.email(),
            'password': fake.password(length=8)
        }
        self.user = User.objects.create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=self.signIn_data['email'],
            password=self.signIn_data['password']
        )
        self.signIn_url = reverse('signin')
        self.refresh_url = reverse('refresh')
        self.signOut_url = reverse('signout')

    def test_SignInViewSet_with_valid_credentials(self):
        """Test sign in API with valid credentials"""

        response = self.client.post(self.signIn_url, self.signIn_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.client.cookies)

    def test_SignInViewSet_with_inactive_user(self):
        """Test sign in API with an inactive user"""

        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.signIn_url, self.signIn_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('no_active_account', response.data['detail'].code)

    def test_SignInViewSet_with_invalid_credentials(self):
        """Test sign in API with invalid credentials"""

        self.signIn_data['password'] = 'wrongpassword'
        response = self.client.post(self.signIn_url, self.signIn_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_SignInViewSet_with_missing_credentials(self):
        """Test sign in API with missing credentials"""

        # Missing email
        response = self.client.post(self.signIn_url,
                                    {'password': self.signIn_data['password']},
                                    format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing password
        response = self.client.post(self.signIn_url,
                                    {'email': self.signIn_data['email']},
                                    format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_RefreshViewSet_with_valid_refresh_token(self):
        """Test refresh API with a valid refresh token"""

        response = self.client.post(self.signIn_url, self.signIn_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.client.cookies)

        refresh_token = response.client.cookies['refresh'].value

        # Cookie is already set on self.client from the Sign-in request above.
        response = self.client.post(self.refresh_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.client.cookies)
        self.assertNotEqual(refresh_token, response.client.cookies['refresh'].value)

    def test_RefreshViewSet_with_invalid_refresh_token(self):
        """Test refresh API with an invalid refresh token"""

        response = self.client.post(self.signIn_url, self.signIn_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.cookies['refresh']="invalid_refresh_token"

        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_RefreshViewSet_with_missing_refresh_token(self):
        """Test refresh API with a missing refresh token"""
        response = self.client.post(self.signIn_url, self.signIn_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.cookies.pop('refresh')

        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh', response.client.cookies)
        self.assertEqual(response.client.cookies['refresh'].value, "")

    def test_SignOutViewSet_with_valid_refresh_token(self):
        """Test sign out API with a valid refresh token"""
        response = self.client.post(self.signIn_url, self.signIn_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.client.cookies)

        refresh_token = response.client.cookies['refresh'].value
        response = self.client.post(self.signOut_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.client.cookies)
        self.assertEqual(response.client.cookies['refresh'].value, "")
        self.assertTrue(BlacklistedToken.objects.filter(token__token=refresh_token).exists())

    def test_SignOutViewSet_with_invalid_refresh_token(self):
        """Test sign out API with an invalid refresh token"""
        response = self.client.post(self.signIn_url, self.signIn_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.cookies['refresh']="invalid_refresh_token"
        response = self.client.post(self.signOut_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Token is invalid', response.data['detail'])

    def test_SignOutViewSet_with_missing_refresh_token(self):
        """Test sign out API with a missing refresh token"""
        response = self.client.post(self.signIn_url, self.signIn_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.cookies.pop('refresh')
        response = self.client.post(self.signOut_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh', response.client.cookies)
        self.assertEqual(response.client.cookies['refresh'].value, "")


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
        self.signIn_url = reverse('signin')

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
