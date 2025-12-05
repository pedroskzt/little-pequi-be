from django.contrib.auth import get_user_model
from django.test import TestCase
from faker.proxy import Faker

from authentication.serializers import MyTokenObtainPairSerializer

fake = Faker()
User = get_user_model()


class MyTokenObtainPairSerializerTests(TestCase):
    """Test cases for MyTokenObtainPairSerializer"""

    def setUp(self):
        self.login_data = {
            'email': fake.email(),
            'password': fake.password(length=8)
        }
        self.user = User.objects.create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=self.login_data['email'],
            password=self.login_data['password'],
        )

    def test_token_is_returned_with_admin_flag_for_admins(self):
        """Test that token is returned with an admin flag set to True for admins"""

        # Set the user as admin
        self.user.is_staff = True
        self.user.save()

        # Confirm the user is an admin
        self.assertTrue(self.user.is_staff)

        token = MyTokenObtainPairSerializer.get_token(self.user)
        self.assertIn('admin', token)
        self.assertTrue(token['admin'])

    def test_token_is_not_returned_with_admin_flag_for_users(self):
        """Test that token is not returned with an admin flag set to True for normal users"""

        # Set the user as admin
        self.user.is_staff = False
        self.user.save()

        # Confirm the user is not an admin
        self.assertFalse(self.user.is_staff)

        token = MyTokenObtainPairSerializer.get_token(self.user)
        self.assertNotIn('admin', token)
