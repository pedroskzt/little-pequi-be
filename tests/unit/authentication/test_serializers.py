from django.contrib.auth import get_user_model
from django.test import TestCase
from faker.proxy import Faker

from authentication.serializers import CustomUserSerializer

fake = Faker()
User = get_user_model()


class CustomUserSerializerTests(TestCase):
    """Test cases for CustomUserSerializer"""

    def setUp(self):
        self.signIn_data = {
            'email': fake.email(),
            'password': fake.password(length=8)
        }
        self.user = User.objects.create_user(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=self.signIn_data['email'],
            password=self.signIn_data['password'],
        )

    def test_serializer_returning_the_is_staff_flag(self):
        """Test that serializer is returning the is_staff flag"""

        user_ser = CustomUserSerializer(instance=self.user)
        self.assertIn('is_staff', user_ser.data)

    def test_serializer_returning_the_is_staff_true_for_admin(self):
        """Test that serializer is returning the is_staff flag set to True for admins"""

        # Set the user as admin
        self.user.is_staff = True
        self.user.save()

        # Confirm the user is an admin
        self.assertTrue(self.user.is_staff)

        user_ser = CustomUserSerializer(instance=self.user)
        self.assertIn('is_staff', user_ser.data)
        self.assertTrue(user_ser.data['is_staff'])

    def test_serializer_returning_the_is_staff_false_for_admin(self):
        """Test that serializer is returning the is_staff flag set to False for normal users"""

        # Set the user as admin
        self.user.is_staff = False
        self.user.save()

        # Confirm the user is not an admin
        self.assertFalse(self.user.is_staff)

        user_ser = CustomUserSerializer(instance=self.user)
        self.assertIn('is_staff', user_ser.data)
        self.assertFalse(user_ser.data['is_staff'])
