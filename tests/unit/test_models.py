from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify
from faker.proxy import Faker

from api.menu.menu_models import Tag, Category, MenuItem, get_next_display_order_available
from tests.helpers import create_image_file, DISHES_1, DISHES_2

fake = Faker()


class TagModelTests(TestCase):
    """Test cases for the Tag model"""

    def setUp(self):
        """Set up test data"""

        self.tag_data = {'title': 'Main Course', 'slug': slugify('Main Course')}
        self.tag = Tag.objects.create(title=self.tag_data['title'])

    def test_tag_creation(self):
        """Test Tag model creation and string representation"""

        self.assertEqual(str(self.tag), self.tag_data['title'])
        self.assertEqual(self.tag.slug, self.tag_data['slug'])
        self.assertEqual(Tag.objects.count(), 1)

    def test_tag_slug_generation(self):
        """Test slug is automatically generated from the title"""

        self.assertEqual(self.tag.slug, slugify(self.tag.title))

    def test_custom_slug(self):
        """Test custom slug is preserved when provided"""

        tag = Tag.objects.create(title="Main Dishes", slug="main")
        self.assertEqual(tag.slug, "main")

    def test_slug_uniqueness(self):
        """Test slug uniqueness constraint"""

        # Trying to create another tag with the same slug should raise an error
        with self.assertRaises(IntegrityError):
            Tag.objects.create(title="Main Course")


class CategoryModelTests(TestCase):
    """Test cases for the Category model"""

    def setUp(self):
        """Set up test data"""

        self.category_data = {'title': 'Main Course', 'slug': slugify('Main Course'), 'display_order': 0}
        self.category = Category.objects.create(title=self.category_data['title'])

    def test_category_creation(self):
        """Test Category model creation and string representation"""

        self.assertEqual(str(self.category), self.category_data['title'])
        self.assertEqual(self.category.slug, self.category_data['slug'])
        self.assertEqual(self.category.display_order, self.category_data['display_order'])
        self.assertEqual(Category.objects.count(), 1)

    def test_category_slug_generation(self):
        """Test slug is automatically generated from the title"""

        self.assertEqual(self.category.slug, slugify(self.category.title))

    def test_custom_slug(self):
        """Test custom slug is preserved when provided"""

        category = Tag.objects.create(title="Main Dishes", slug="main")
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

        self.tag1 = Tag.objects.create(title="Brazilian")
        self.tag2 = Tag.objects.create(title="Vegetarian")

        self.category1 = Category.objects.create(title="Main Course")
        self.category2 = Category.objects.create(title="Appetizer")

        self.menu_item_data = {
            'title': fake.word(ext_word_list=DISHES_1),
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'description': fake.sentence(),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
            'category': self.category1
        }

        self.menu_item = MenuItem.objects.create(**self.menu_item_data)
        self.menu_item.tags.add(self.tag1)

    def test_menu_item_creation(self):
        """Test MenuItem model creation and string representation"""

        self.assertEqual(self.menu_item.title, self.menu_item_data['title'])
        self.assertEqual(self.menu_item.price, self.menu_item_data['price'])
        self.assertEqual(self.menu_item.description, self.menu_item_data['description'])
        self.assertEqual(self.menu_item.featured, self.menu_item_data['featured'])
        self.assertEqual(self.menu_item.delivery, self.menu_item_data['delivery'])
        self.assertEqual(self.menu_item.category, self.category1)
        self.assertEqual(self.menu_item.tags.count(), 1)
        self.assertIn(self.tag1, self.menu_item.tags.all())

    @patch('storages.backends.gcloud.GoogleCloudStorage.save')
    def test_menu_item_image_upload_to_gcs(self, mock_gcs_save):
        """Test image upload to Google Cloud Storage"""

        # Mock the GCS save method to return a fake path
        mock_gcs_save.return_value = f'{settings.MENU_ITEM_MEDIA_ROOT}test_gcs_image.png'

        # Create a menu item with an image
        test_image = create_image_file(name='test_gcs_image.png', mode='L')

        menu_item = MenuItem.objects.create(
            title=fake.word(ext_word_list=DISHES_2),
            price=fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            description=fake.sentence(),
            featured=fake.pybool(),
            delivery=fake.pybool(),
            category=self.category1,
            image=test_image
        )

        # Verify that the GCS save method was called
        self.assertTrue(mock_gcs_save.called)

        # Verify that the image field is set correctly
        self.assertIsNotNone(menu_item.image)
        self.assertIn('test_gcs_image.png', menu_item.image.name)

        # Verify the image name contains the expected path
        self.assertTrue(menu_item.image.name.startswith(settings.MENU_ITEM_MEDIA_ROOT))

    @patch('storages.backends.gcloud.GoogleCloudStorage.exists')
    @patch('storages.backends.gcloud.GoogleCloudStorage.save')
    def test_menu_item_image_exists_in_gcs(self, mock_gcs_save, mock_gcs_exists):
        """Test that uploaded image exists in Google Cloud Storage"""

        # Mock the storage backend
        image_name = f'{settings.MENU_ITEM_MEDIA_ROOT}test_exists.png'
        mock_gcs_save.return_value = image_name
        mock_gcs_exists.return_value = True

        # Create a menu item with an image
        test_image = create_image_file(name='test_exists.png', mode='L')
        menu_item = MenuItem.objects.create(
            title=fake.word(ext_word_list=DISHES_2),
            price=fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            description=fake.sentence(),
            featured=fake.pybool(),
            delivery=fake.pybool(),
            category=self.category1,
            image=test_image
        )

        # Check if the image exists in storage
        image_exists = menu_item.image.storage.exists(menu_item.image.name)

        # Verify the exists method was called
        self.assertTrue(mock_gcs_exists.called)
        self.assertTrue(image_exists)

    def test_menu_item_string_representation(self):
        """Test string representation of MenuItem"""

        self.assertEqual(str(self.menu_item), self.menu_item_data['title'])

    def test_menu_item_multiple_tags(self):
        """Test MenuItem can have multiple tags"""

        self.menu_item.tags.add(self.tag2)

        self.assertEqual(self.menu_item.tags.count(), 2)
        self.assertIn(self.tag1, self.menu_item.tags.all())
        self.assertIn(self.tag2, self.menu_item.tags.all())

    def test_menu_item_single_category(self):
        """Test MenuItem can belong to a single category"""

        self.assertEqual(self.menu_item.category, self.category1)
        self.assertNotEqual(self.menu_item.category, self.category2)

        self.menu_item.category = self.category2

        self.assertEqual(self.menu_item.category, self.category2)
        self.assertNotEqual(self.menu_item.category, self.category1)

    def test_menu_item_invalid_price(self):
        """Test MenuItem validation with invalid price"""

        with self.assertRaises(ValidationError):
            MenuItem.objects.create(
                title="Invalid Price",
                price="invalid_price"
            )


class GetNextDisplayOrderAvailableTests(TestCase):
    """Test cases for the get_next_display_order_available function"""

    def test_no_categories_returns_zero(self):
        """Test that function returns 0 when no categories exist"""
        result = get_next_display_order_available()
        self.assertEqual(result, 0)

    def test_single_category_at_zero(self):
        """Test with a single category at display_order 0"""
        Category.objects.create(title="First Category", display_order=0)
        result = get_next_display_order_available()
        self.assertEqual(result, 1)

    def test_sequential_categories(self):
        """Test with sequential categories (0, 1, 2)"""
        Category.objects.create(title="Category 1", display_order=0)
        Category.objects.create(title="Category 2", display_order=1)
        Category.objects.create(title="Category 3", display_order=2)
        result = get_next_display_order_available()
        self.assertEqual(result, 3)

    def test_gap_in_sequence(self):
        """Test with a gap in the sequence (0, 1, 3) - missing 2"""
        Category.objects.create(title="Category 1", display_order=0)
        Category.objects.create(title="Category 2", display_order=1)
        Category.objects.create(title="Category 4", display_order=3)
        result = get_next_display_order_available()
        self.assertEqual(result, 2)

    def test_gap_at_beginning(self):
        """Test with categories starting from 1 (gap at 0)"""
        Category.objects.create(title="Category 2", display_order=1)
        Category.objects.create(title="Category 3", display_order=2)
        result = get_next_display_order_available()
        self.assertEqual(result, 0)

    def test_gap_in_middle(self):
        """Test with a gap in the middle (0, 1, 2, 4, 5) - missing 3"""
        Category.objects.create(title="Category 1", display_order=0)
        Category.objects.create(title="Category 2", display_order=1)
        Category.objects.create(title="Category 3", display_order=2)
        Category.objects.create(title="Category 5", display_order=4)
        Category.objects.create(title="Category 6", display_order=5)
        result = get_next_display_order_available()
        self.assertEqual(result, 3)

    def test_single_category_not_at_zero(self):
        """Test with a single category at non-zero position"""
        Category.objects.create(title="Category", display_order=5)
        result = get_next_display_order_available()
        # Should return the first missing number (0)
        self.assertEqual(result, 0)

    def test_continuous_sequence_without_zero(self):
        """Test with continuous sequence not starting at 0 (5, 6, 7)"""
        Category.objects.create(title="Category 6", display_order=5)
        Category.objects.create(title="Category 7", display_order=6)
        Category.objects.create(title="Category 8", display_order=7)
        result = get_next_display_order_available()
        # Should return the first missing number: 0
        self.assertEqual(result, 0)

    def test_two_categories_with_gap(self):
        """Test with two categories with a gap (0, 2) - missing 1"""
        Category.objects.create(title="Category 1", display_order=0)
        Category.objects.create(title="Category 3", display_order=2)
        result = get_next_display_order_available()
        self.assertEqual(result, 1)

    def test_category_auto_assignment(self):
        """Test that new categories get correct display_order automatically"""
        # First category should get 0
        cat1 = Category.objects.create(title="First")
        self.assertEqual(cat1.display_order, 0)

        # Second should get 1
        cat2 = Category.objects.create(title="Second")
        self.assertEqual(cat2.display_order, 1)

        # Delete the second category to create a gap
        cat2.delete()

        # Third should fill the gap (get 1)
        cat3 = Category.objects.create(title="Third")
        self.assertEqual(cat3.display_order, 1)

        # Fourth should get 2
        cat4 = Category.objects.create(title="Fourth")
        self.assertEqual(cat4.display_order, 2)