from django.contrib.auth import get_user_model, authenticate
from django.test import TestCase
from faker import Faker

User = get_user_model()
fake = Faker()


class UserBackendTests(TestCase):
    """Test UserBackend authenticate method"""

    def setUp(self):
        """Set up test data"""

        self.login_data = {
            'email': fake.email(),
            'password': fake.password(length=8)
        }

        user_data = {
            'email': self.login_data['email'],
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'password': self.login_data['password']
        }

        self.user = User.objects.create_user(**user_data)

    def test_user_backend_authenticate(self):
        """Test UserBackend authenticate method"""

        # Authenticate with email
        self.assertEqual(authenticate(email=self.login_data['email'], password=self.login_data['password']), self.user)

        # Authenticate with username
        self.assertEqual(authenticate(username=self.login_data['email'], password=self.login_data['password']), self.user)

    def test_user_backend_authenticate_invalid_credentials(self):
        """Test UserBackend authenticate method with invalid credentials"""

        # Wrong Password
        self.assertIsNone(authenticate(email=self.login_data['email'], password="wrongPass"))

        # Wrong Email
        self.assertIsNone(authenticate(email="wrongEmail@example.com", password=self.login_data['password']))

        # Wrong Username
        self.assertIsNone(authenticate(username="wrongEmail@example.com", password=self.login_data['password']))

    def test_user_backend_authenticate_missing_required_fields(self):
        """Test UserBackend authenticate method with missing required fields"""

        # Authenticate with an email and missing password
        self.assertIsNone(authenticate(email=self.login_data['email']))

        # Authenticate with a username and missing password
        self.assertIsNone(authenticate(username=self.login_data['email']))

        # Authenticate missing an email or a username
        self.assertIsNone(authenticate(password=self.login_data['password']))

    def test_user_backend_authenticate_inactive_user(self):
        """Test UserBackend authenticate method with an inactive user"""

        self.user.is_active = False
        self.user.save()

        # Authenticate with email
        self.assertIsNone(authenticate(email=self.login_data['email'], password=self.login_data['password']))

        # Authenticate with username
        self.assertIsNone(authenticate(username=self.login_data['email'], password=self.login_data['password']))
