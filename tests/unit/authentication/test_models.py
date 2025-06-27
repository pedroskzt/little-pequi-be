from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.template.defaultfilters import length
from django.test import TestCase
from faker.proxy import Faker

User = get_user_model()
fake = Faker()


class UserModelTests(TestCase):
    """Test User model"""

    def test_user_creation(self):
        """Test User object creation with correct data for regular user and superuser"""

        user_data = {
            'email': fake.email(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'password': fake.password(length=8)
        }

        user = User.objects.create_user(**user_data)

        superuser_data = {

            'email': fake.email(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'password': fake.password(length=8)
        }

        superuser = User.objects.create_superuser(**superuser_data)

        # Test regular user attributes
        self.assertEqual(user.email, user_data['email'])
        self.assertEqual(user.username, user_data['email'])
        self.assertEqual(user.first_name, user_data['first_name'])
        self.assertEqual(user.last_name, user_data['last_name'])
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertEqual(str(user), user_data['email'])

        # Test superuser attributes
        self.assertEqual(superuser.email, superuser_data['email'])
        self.assertEqual(superuser.username, superuser_data['email'])
        self.assertEqual(superuser.first_name, superuser_data['first_name'])
        self.assertEqual(superuser.last_name, superuser_data['last_name'])
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
        self.assertEqual(str(superuser), superuser_data['email'])

    def test_user_creation_missing_required_fields(self):
        """Test User object creation with missing required fields"""

        # Missing email
        with transaction.atomic():
            with self.assertRaises(TypeError):
                User.objects.create_user(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    password=fake.password(length=8)
                )

        # Missing first_name
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                User.objects.create_user(
                    email=fake.email(),
                    last_name=fake.last_name(),
                    password=fake.password(length=8)
                )

        # Missing last_name
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                User.objects.create_user(
                    email=fake.email(),
                    first_name=fake.first_name(),
                    password=fake.password(length=8)
                )

        # Missing password
        with transaction.atomic():
            with self.assertRaises(TypeError):
                User.objects.create_user(
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )

    def test_user_creation_invalid_data(self):
        """Test User object creation with invalid data"""

        # Empty email
        with transaction.atomic():
            with self.assertRaises(ValueError):
                User.objects.create_user(
                    email="",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    password=fake.password(length=8)
                )

        # Not valid email
        with transaction.atomic():
            with self.assertRaises(ValueError):
                User.objects.create_user(
                    email="this is not an email",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    password=fake.password(length=8)
                )

        # Superuser with is_staff false
        with transaction.atomic():
            with self.assertRaises(ValueError):
                User.objects.create_superuser(
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    password=fake.password(length=8),
                    is_staff=False,
                    is_superuser=True
                )

        # Superuser with is_superuser false
        with transaction.atomic():
            with self.assertRaises(ValueError):
                User.objects.create_superuser(
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    password=fake.password(length=8),
                    is_staff=True,
                    is_superuser=False
                )

    def test_user_email_uniqueness(self):
        """Test User email uniqueness"""

        user_1 = User.objects.create_user(
            email="regularuser@example.com",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password=fake.password(length=8)
        )

        with self.assertRaises(IntegrityError):
            user_2 = User.objects.create_user(
                email="regularuser@example.com",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password=fake.password(length=8)
            )
