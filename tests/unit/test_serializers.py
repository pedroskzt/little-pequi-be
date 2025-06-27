from os import remove as remove_file

from PIL import Image
from django.conf import settings
from django.db import transaction
from django.test import TestCase
from django.utils.text import slugify
from faker.proxy import Faker

from api.menu.menu_models import MenuItem, Category
from api.menu.menu_serializers import MenuItemSerializer, CategorySerializer
from tests.helpers import create_image_file, DISHES_1, DISHES_2

fake = Faker()


class CategorySerializerTests(TestCase):
    """Test cases for CategorySerializer"""

    def setUp(self):
        """Set up test data"""

        self.category = Category.objects.create(title="Main Course")

        self.serializer = CategorySerializer(instance=self.category)

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields"""

        data = self.serializer.data

        expected_fields = ['id', 'title', 'slug']

        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_serialized_data(self):
        """Test serializer with valid data"""

        data = {
            'id': self.category.id,
            'title': self.category.title,
            'slug': self.category.slug,
        }
        self.assertEqual(self.serializer.data, data)

    def test_serializer_create(self):
        """Test creating a new category through serializer"""

        new_category_data = {
            'title': 'To Share'
        }

        serializer = CategorySerializer(data=new_category_data)
        self.assertTrue(serializer.is_valid())

        new_category = serializer.save()

        # Check the new item was created correctly
        self.assertEqual(new_category.title, new_category_data.get('title'))
        self.assertEqual(new_category.slug, slugify(new_category_data.get('title')))

    def test_serializer_validation_missing_required_fields(self):
        """Test serializer validation with missing required fields"""

        # Missing Title
        with transaction.atomic():
            serializer = CategorySerializer(data={})
            self.assertFalse(serializer.is_valid())
            self.assertIn('title', serializer.errors)

    def test_serializer_validation_invalid_data(self):
        """Test serializer validation with invalid data"""

        # Invalid Title
        with transaction.atomic():
            serializer = CategorySerializer(data={'title': ''})
            self.assertFalse(serializer.is_valid())
            self.assertIn('title', serializer.errors)

    def test_serializer_update(self):
        """Test updating an existing category through serializer"""
        category_id = self.category.id
        updated_data = {
            'title': 'Prato Principal',
            'slug': slugify('Prato Principal')
        }
        serializer = CategorySerializer(instance=self.category, data=updated_data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        # Check the existing category if it was updated correctly
        self.assertEqual(self.category.id, category_id)
        self.assertEqual(self.category.title, updated_data.get('title'))
        self.assertEqual(self.category.slug, self.category.slug)

    def test_serializer_partial_update(self):
        """Test updating an existing category through serializer with partial data"""

        expected_updated_data = {
            'id': self.category.id,
            'title': 'Prato Principal',
            'slug': self.category.slug
        }

        serializer = CategorySerializer(instance=self.category, data={'title': 'Prato Principal'}, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Check the existing category if it was updated correctly
        self.assertEqual(self.category.id, expected_updated_data.get('id'))
        self.assertEqual(self.category.title, expected_updated_data.get('title'))
        self.assertEqual(self.category.slug, expected_updated_data.get('slug'))


class MenuItemSerializerTests(TestCase):
    """Test cases for MenuItemSerializer"""

    def setUp(self):
        """Set up test data"""

        self.category1 = Category.objects.create(title="Main Course")
        self.category2 = Category.objects.create(title="Vegetarian")

        self.menu_item_data = {
            'title': fake.word(ext_word_list=DISHES_1),
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
            'image': create_image_file(name='test_image.png', mode='L')
        }

        self.menu_item = MenuItem.objects.create(**self.menu_item_data)
        self.menu_item.category.add(self.category1)

        self.serializer = MenuItemSerializer(instance=self.menu_item)

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields"""

        data = self.serializer.data

        expected_fields = ['id', 'title', 'price', 'featured', 'delivery', 'category', 'image']

        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_serialized_data(self):
        """Test serializer with valid data"""

        expected_data = {
            'id': self.menu_item.id,
            'title': self.menu_item.title,
            'price': str(self.menu_item.price),
            'featured': self.menu_item.featured,
            'delivery': self.menu_item.delivery,
            'image': self.menu_item.image.url,
            'category': [self.category1.id],
        }
        self.assertEqual(self.serializer.data, expected_data)

    def test_serializer_create(self):
        """Test creating a new menu item through serializer"""

        new_item_data = {
            'title': fake.word(ext_word_list=DISHES_2),
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
            'category': [self.category2.id],
            'image': create_image_file(name='test_image.png', mode='L')
        }

        serializer = MenuItemSerializer(data=new_item_data)
        self.assertTrue(serializer.is_valid())

        new_item = serializer.save()

        # Check the new item was created correctly
        self.assertEqual(new_item.title, new_item_data['title'])
        self.assertEqual(new_item.price, new_item_data['price'])
        self.assertEqual(new_item.featured, new_item_data['featured'])
        self.assertEqual(new_item.delivery, new_item_data['delivery'])
        self.assertEqual(new_item.category.count(), 1)
        self.assertEqual(new_item.category.first(), self.category2)

    def test_serializer_validation_missing_required_fields(self):
        """Test serializer validation with missing required fields"""

        new_item_data = {
            'title': fake.word(ext_word_list=DISHES_2),
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
            'category': [self.category2.id],
            'image': create_image_file(name='test_image.png', mode='L')
        }

        # Missing Title
        with transaction.atomic():
            temp = new_item_data.pop('title')
            serializer = MenuItemSerializer(data=new_item_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('title', serializer.errors)
            new_item_data['title'] = temp

        # Missing Price
        with transaction.atomic():
            temp = new_item_data.pop('price')
            serializer = MenuItemSerializer(data=new_item_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('price', serializer.errors)
            new_item_data['price'] = temp

        # Missing Featured
        with transaction.atomic():
            temp = new_item_data.pop('featured')
            serializer = MenuItemSerializer(data=new_item_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('featured', serializer.errors)
            new_item_data['featured'] = temp

        # Missing Delivery
        with transaction.atomic():
            temp = new_item_data.pop('delivery')
            serializer = MenuItemSerializer(data=new_item_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('delivery', serializer.errors)
            new_item_data['delivery'] = temp

        # Missing Image
        with transaction.atomic():
            new_item_data.pop('image')
            serializer = MenuItemSerializer(data=new_item_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('image', serializer.errors)

    def test_serializer_validation_invalid_data(self):
        """Test serializer validation with invalid data"""

        new_item_data = {
            'title': fake.word(ext_word_list=DISHES_2),
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
            'category': [self.category2.id],
            'image': create_image_file(name='test_image.png', mode='L')
        }

        # Invalid Title
        with transaction.atomic():
            temp = new_item_data.pop('title')
            new_item_data['title'] = ''
            serializer = MenuItemSerializer(data=new_item_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('title', serializer.errors)
            new_item_data['title'] = temp

        # Invalid Price
        with transaction.atomic():
            temp = new_item_data.pop('price')
            new_item_data['price'] = 'invalid_price'
            serializer = MenuItemSerializer(data=new_item_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('price', serializer.errors)
            new_item_data['price'] = temp

        # Invalid Featured
        with transaction.atomic():
            temp = new_item_data.pop('featured')
            new_item_data['featured'] = 'invalid_featured'
            serializer = MenuItemSerializer(data=new_item_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('featured', serializer.errors)
            new_item_data['featured'] = temp

        # Invalid Delivery
        with transaction.atomic():
            temp = new_item_data.pop('delivery')
            new_item_data['delivery'] = "invalid_delivery"
            serializer = MenuItemSerializer(data=new_item_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('delivery', serializer.errors)
            new_item_data['delivery'] = temp

        # Invalid Category
        with transaction.atomic():
            temp = new_item_data.pop('category')
            new_item_data['category'] = "invalid_category_id"
            serializer = MenuItemSerializer(data=new_item_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('category', serializer.errors)

        # Category does not exist
        with transaction.atomic():
            new_item_data['category'] = [999]
            serializer = MenuItemSerializer(data=new_item_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('category', serializer.errors)
            new_item_data['category'] = temp

        # Invalid Image
        with transaction.atomic():
            new_item_data['image'] = create_image_file(name='test_image.png', empty_image=True)
            serializer = MenuItemSerializer(data=new_item_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('image', serializer.errors)

    def test_serializer_update(self):
        """Test updating an existing menu item through serializer"""

        menu_item_id = self.menu_item.id
        updated_data = {
            'title': fake.word(ext_word_list=DISHES_2),
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
            'image': create_image_file(name='test_image_updated.png', mode='L'),
            'category': [self.category1.id, self.category2.id],
        }

        serializer = MenuItemSerializer(instance=self.menu_item, data=updated_data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Check the existing menu item if it was updated correctly
        self.assertEqual(self.menu_item.id, menu_item_id)
        self.assertEqual(self.menu_item.title, updated_data.get('title'))
        self.assertEqual(self.menu_item.price, updated_data.get('price'))
        self.assertEqual(self.menu_item.featured, updated_data.get('featured'))
        self.assertEqual(self.menu_item.delivery, updated_data.get('delivery'))
        self.assertEqual(self.menu_item.category.count(), len(updated_data.get('category')))
        self.assertEqual(str(self.menu_item.image), f'{settings.MENU_ITEM_MEDIA_ROOT}test_image_updated.png')
        self.assertIn(self.category1, self.menu_item.category.all())
        self.assertIn(self.category2, self.menu_item.category.all())

        # Verify if the updated image was uploaded and saved with the expected filename
        img = Image.open(self.menu_item.image.path)
        self.assertIsNone(img.verify())
        remove_file(self.menu_item.image.path)

    def test_serializer_partial_update(self):
        """Test updating an existing menu item through serializer with partial data"""

        partial_update_data = {
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
        }
        expected_updated_data = {
            'id': self.menu_item.id,
            'title': self.menu_item.title,
            'price': partial_update_data['price'],
            'featured': partial_update_data['featured'],
            'delivery': partial_update_data['delivery'],
            'image': self.menu_item.image.url,
            'category': [self.menu_item.category.first().id],
        }

        serializer = MenuItemSerializer(instance=self.menu_item, data=partial_update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Check the existing menu item if it was updated correctly
        self.assertEqual(self.menu_item.id, expected_updated_data.get('id'))
        self.assertEqual(self.menu_item.title, expected_updated_data.get('title'))
        self.assertEqual(self.menu_item.price, expected_updated_data.get('price'))
        self.assertEqual(self.menu_item.featured, expected_updated_data.get('featured'))
        self.assertEqual(self.menu_item.delivery, expected_updated_data.get('delivery'))
        self.assertEqual(self.menu_item.image.url, expected_updated_data.get('image'))
        self.assertEqual(self.menu_item.category.count(), len(expected_updated_data.get('category')))
        self.assertIn(self.category1, self.menu_item.category.all())
