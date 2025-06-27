from os import remove as remove_file

from PIL import Image
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify
from faker.proxy import Faker

from api.menu.menu_models import Category, MenuItem
from tests.helpers import create_image_file, DISHES_1, DISHES_2

fake = Faker()


class CategoryModelTests(TestCase):
    """Test cases for the Category model"""

    def setUp(self):
        """Set up test data"""

        self.category_data = {'title': 'Main Course', 'slug': slugify('Main Course')}
        self.category = Category.objects.create(title=self.category_data['title'])

    def test_category_creation(self):
        """Test Category model creation and string representation"""

        self.assertEqual(str(self.category), self.category_data['title'])
        self.assertEqual(self.category.slug, self.category_data['slug'])

    def test_category_slug_generation(self):
        """Test slug is automatically generated from the title"""

        self.assertEqual(self.category.slug, slugify(self.category.title))

    def test_custom_slug(self):
        """Test custom slug is preserved when provided"""

        category = Category.objects.create(title="Main Dishes", slug="main")
        self.assertEqual(category.slug, "main")

    def test_slug_uniqueness(self):
        """Test slug uniqueness constraint"""

        # Trying to create another category with the same slug should raise an error
        with self.assertRaises(IntegrityError):
            Category.objects.create(title="Main Course")


class MenuItemModelTests(TestCase):
    """Test cases for the MenuItem model"""

    def setUp(self):
        """Set up test data"""

        self.category1 = Category.objects.create(title="Main Course")
        self.category2 = Category.objects.create(title="Vegetarian")

        self.menu_item_data = {
            'title': fake.word(ext_word_list=DISHES_1),
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
            'image': create_image_file(name='test_image.png', empty_image=True)
        }

        self.menu_item = MenuItem.objects.create(**self.menu_item_data)
        self.menu_item.category.add(self.category1)

    def test_menu_item_creation(self):
        """Test MenuItem model creation and string representation"""

        self.assertEqual(self.menu_item.title, self.menu_item_data['title'])
        self.assertEqual(self.menu_item.price, self.menu_item_data['price'])
        self.assertIn(self.category1, self.menu_item.category.all())
        self.assertEqual(self.menu_item.featured, self.menu_item_data['featured'])
        self.assertEqual(self.menu_item.delivery, self.menu_item_data['delivery'])

    def test_menu_item_image_upload(self):
        """Test image upload to the correct path with the expected filename"""

        menu_item = MenuItem.objects.create(
            title=fake.word(ext_word_list=DISHES_2),
            price=fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            featured=fake.pybool(),
            delivery=fake.pybool(),
            image=create_image_file(name='test_image_upload.png', mode='L')
        )

        # Verify the image was uploaded to the correct path with the expected filename
        self.assertEqual(str(menu_item.image), f'{settings.MENU_ITEM_MEDIA_ROOT}test_image_upload.png')

        img = Image.open(menu_item.image.path)

        # Verify the image was uploaded and saved with the expected filename
        self.assertIsNone(img.verify())
        remove_file(menu_item.image.path)

    def test_menu_item_string_representation(self):
        """Test string representation of MenuItem"""

        self.assertEqual(str(self.menu_item), self.menu_item_data['title'])

    def test_menu_item_multiple_categories(self):
        """Test MenuItem can belong to multiple categories"""

        self.menu_item.category.add(self.category2)

        self.assertEqual(self.menu_item.category.count(), 2)
        self.assertIn(self.category1, self.menu_item.category.all())
        self.assertIn(self.category2, self.menu_item.category.all())

    def test_menu_item_invalid_price(self):
        """Test MenuItem validation with invalid price"""

        with self.assertRaises(ValidationError):
            MenuItem.objects.create(
                title="Invalid Price",
                price="invalid_price"
            )
