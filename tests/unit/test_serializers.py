from unittest.mock import patch

from django.conf import settings
from django.db import transaction
from django.test import TestCase
from django.utils.text import slugify
from faker.proxy import Faker

from api.menu.menu_models import MenuItem, Tag, Category, get_next_display_order_available
from api.menu.menu_serializers import MenuItemSerializer, TagSerializer, CategorySerializer, MenuItemImageSerializer
from tests.helpers import create_image_file, DISHES_1, DISHES_2

fake = Faker()


class TagSerializerTests(TestCase):
    """Test cases for TagSerializer"""

    def setUp(self):
        """Set up test data"""

        self.tag = Tag.objects.create(title="Main Course")

        self.serializer = TagSerializer(instance=self.tag)

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields"""

        data = self.serializer.data

        expected_fields = ['id', 'title', 'slug']

        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_serialized_data(self):
        """Test serializer with valid data"""

        data = {
            'id': self.tag.id,
            'title': self.tag.title,
            'slug': self.tag.slug,
        }
        self.assertEqual(self.serializer.data, data)

    def test_serializer_create(self):
        """Test creating a new tag through serializer"""

        new_tag_data = {
            'title': 'To Share'
        }

        serializer = TagSerializer(data=new_tag_data)
        self.assertTrue(serializer.is_valid())

        new_tag = serializer.save()

        # Check the new item was created correctly
        self.assertEqual(new_tag.title, new_tag_data.get('title'))
        self.assertEqual(new_tag.slug, slugify(new_tag_data.get('title')))

    def test_serializer_validation_missing_required_fields(self):
        """Test serializer validation with missing required fields"""

        # Missing Title
        with transaction.atomic():
            serializer = TagSerializer(data={})
            self.assertFalse(serializer.is_valid())
            self.assertIn('title', serializer.errors)

    def test_serializer_validation_invalid_data(self):
        """Test serializer validation with invalid data"""

        # Invalid Title
        with transaction.atomic():
            serializer = TagSerializer(data={'title': ''})
            self.assertFalse(serializer.is_valid())
            self.assertIn('title', serializer.errors)

    def test_serializer_update(self):
        """Test updating an existing tag through serializer"""
        tag_id = self.tag.id
        updated_data = {
            'title': 'Prato Principal',
            'slug': slugify('Prato Principal')
        }
        serializer = TagSerializer(instance=self.tag, data=updated_data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        # Check the existing tags if it was updated correctly
        self.assertEqual(self.tag.id, tag_id)
        self.assertEqual(self.tag.title, updated_data.get('title'))
        self.assertEqual(self.tag.slug, self.tag.slug)

    def test_serializer_partial_update(self):
        """Test updating an existing tag through serializer with partial data"""

        expected_updated_data = {
            'id': self.tag.id,
            'title': 'Prato Principal',
            'slug': self.tag.slug
        }

        serializer = TagSerializer(instance=self.tag, data={'title': 'Prato Principal'}, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Check the existing tags if it was updated correctly
        self.assertEqual(self.tag.id, expected_updated_data.get('id'))
        self.assertEqual(self.tag.title, expected_updated_data.get('title'))
        self.assertEqual(self.tag.slug, expected_updated_data.get('slug'))


class CategorySerializerTests(TestCase):
    """Test cases for CategorySerializer"""

    def setUp(self):
        """Set up test data"""

        self.category = Category.objects.create(title="Main Course")

        self.serializer = CategorySerializer(instance=self.category)

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields"""

        data = self.serializer.data

        expected_fields = ['id', 'title', 'slug', 'menu_items', 'display_order']
        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_serialized_data(self):
        """Test serializer with valid data"""

        data = {
            'id': self.category.id,
            'title': self.category.title,
            'slug': self.category.slug,
            'menu_items': [],
            'display_order': self.category.display_order
        }
        self.assertEqual(self.serializer.data, data)

    def test_serializer_create(self):
        """Test creating a new category through serializer"""

        new_category_data = {
            'title': 'To Share'
        }

        # Get the next available display order for the new category before creating it
        next_display_order = get_next_display_order_available()

        serializer = CategorySerializer(data=new_category_data)
        self.assertTrue(serializer.is_valid())

        new_category = serializer.save()

        # Check the new item was created correctly
        self.assertEqual(new_category.title, new_category_data.get('title'))
        self.assertEqual(new_category.slug, slugify(new_category_data.get('title')))
        self.assertEqual(new_category.display_order, next_display_order)

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
        category_slug = self.category.slug

        updated_data = {
            'title': 'Prato Principal',
            'display_order': get_next_display_order_available()
        }

        serializer = CategorySerializer(instance=self.category, data=updated_data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Check the existing categories if it was updated correctly
        self.assertEqual(self.category.id, category_id)
        self.assertEqual(self.category.title, updated_data.get('title'))
        self.assertEqual(self.category.slug, category_slug)
        self.assertEqual(self.category.display_order, updated_data.get('display_order'))

    def test_serializer_partial_update(self):
        """Test updating an existing category through serializer with partial data"""

        expected_updated_data = {
            'id': self.category.id,
            'title': 'Prato Principal',
            'slug': self.category.slug,
            'display_order': self.category.display_order
        }

        serializer = CategorySerializer(instance=self.category, data={'title': expected_updated_data.get('title')},
                                        partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Check the existing tags if it was updated correctly
        self.assertEqual(self.category.id, expected_updated_data.get('id'))
        self.assertEqual(self.category.title, expected_updated_data.get('title'))
        self.assertEqual(self.category.slug, expected_updated_data.get('slug'))
        self.assertEqual(self.category.display_order, expected_updated_data.get('display_order'))


@patch('storages.backends.gcloud.GoogleCloudStorage.exists')
class MenuItemSerializerTests(TestCase):
    """Test cases for MenuItemSerializer"""

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
            'category': self.category1,
        }

        self.menu_item = MenuItem.objects.create(**self.menu_item_data)
        self.menu_item.tags.add(self.tag1)

        self.serializer = MenuItemSerializer(instance=self.menu_item)

    def test_serializer_contains_expected_fields(self, mock_gcs_exists):
        """Test that serializer contains all expected fields"""

        data = self.serializer.data

        expected_fields = ['id', 'title', 'price', 'description', 'featured', 'delivery', 'category', 'tags', 'image']

        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_serialized_data(self, mock_gcs_exists):
        """Test serializer with valid data"""
        expected_data = {
            'id': self.menu_item.id,
            'title': self.menu_item.title,
            'price': str(self.menu_item.price),
            'description': self.menu_item.description,
            'featured': self.menu_item.featured,
            'delivery': self.menu_item.delivery,
            'category': {
                'id': self.category1.id,
                'title': self.category1.title,
                'slug': self.category1.slug,
                'menu_items': [],
                'display_order': self.category1.display_order
            },
            'image': None,
            'tags': [{
                'id': self.tag1.id,
                'title': self.tag1.title,
                'slug': self.tag1.slug
            }],
        }

        self.assertEqual(self.serializer.data, expected_data)

    def test_serializer_create(self, mock_gcs_exists):
        """Test creating a new menu item through serializer"""

        new_item_data = {
            'title': fake.word(ext_word_list=DISHES_2),
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'description': fake.sentence(),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
            'category': self.category2.id,
            'tags': [self.tag2.id],
        }

        context = {
            'tags': new_item_data['tags'],
            'category': new_item_data['category']
        }

        serializer = MenuItemSerializer(data=new_item_data, context=context)
        self.assertTrue(serializer.is_valid())

        new_item = serializer.save()

        # Check the new item was created correctly
        self.assertEqual(new_item.title, new_item_data['title'])
        self.assertEqual(new_item.price, new_item_data['price'])
        self.assertEqual(new_item.description, new_item_data['description'])
        self.assertEqual(new_item.featured, new_item_data['featured'])
        self.assertEqual(new_item.delivery, new_item_data['delivery'])
        self.assertEqual(new_item.tags.count(), 1)
        self.assertEqual(new_item.tags.first(), self.tag2)
        self.assertEqual(new_item.category, self.category2)
        self.assertIsNone(new_item.image.name)

    def test_serializer_validation_missing_required_fields(self, mock_gcs_exists):
        """Test serializer validation with missing required fields"""

        new_item_data = {
            'title': fake.word(ext_word_list=DISHES_2),
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'description': fake.sentence(),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
            'tags': [self.tag2.id],
            'category': self.category2.id,
        }

        context = {
            'tags': new_item_data['tags'],
            'category': new_item_data['category']
        }

        # Missing Title
        with transaction.atomic():
            temp = new_item_data.pop('title')
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('title', serializer.errors)
            new_item_data['title'] = temp

        # Missing Price
        with transaction.atomic():
            temp = new_item_data.pop('price')
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('price', serializer.errors)
            new_item_data['price'] = temp

        # Missing Description
        with transaction.atomic():
            temp = new_item_data.pop('description')
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('description', serializer.errors)
            new_item_data['description'] = temp

        # Missing Category
        with transaction.atomic():
            temp = context.pop('category')
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('category', serializer.errors)
            context['category'] = temp

    def test_serializer_validation_invalid_data(self, mock_gcs_exists):
        """Test serializer validation with invalid data"""

        new_item_data = {
            'title': fake.word(ext_word_list=DISHES_2),
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'description': fake.sentence(),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
            'tags': [self.tag2.id],
            'category': self.category2.id,
        }

        context = {
            'tags': new_item_data['tags'],
            'category': new_item_data['category']
        }

        # Invalid Title
        with transaction.atomic():
            temp = new_item_data.pop('title')
            new_item_data['title'] = ''
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('title', serializer.errors)
            new_item_data['title'] = temp

        # Invalid Price
        with transaction.atomic():
            temp = new_item_data.pop('price')
            new_item_data['price'] = 'invalid_price'
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('price', serializer.errors)
            new_item_data['price'] = temp

        # Invalid Description
        with transaction.atomic():
            temp = new_item_data.pop('description')
            new_item_data['description'] = ''
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('description', serializer.errors)
            new_item_data['description'] = temp

        # Invalid Featured
        with transaction.atomic():
            temp = new_item_data.pop('featured')
            new_item_data['featured'] = 'invalid_featured'
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('featured', serializer.errors)
            new_item_data['featured'] = temp

        # Invalid Delivery
        with transaction.atomic():
            temp = new_item_data.pop('delivery')
            new_item_data['delivery'] = "invalid_delivery"
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('delivery', serializer.errors)
            new_item_data['delivery'] = temp

        # Invalid Category
        with transaction.atomic():
            temp = context.pop('category')
            context['category'] = "invalid_category_id"
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('category', serializer.errors)
            context['category'] = temp

        # Invalid Tag
        with transaction.atomic():
            temp = context.pop('tags')
            context['tags'] = "invalid_category_id"
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('tags', serializer.errors)
            context['tags'] = temp

        # Category does not exist
        with transaction.atomic():
            temp = context.pop('category')
            context['category'] = 999
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('category', serializer.errors)
            context['category'] = temp

        # Tag does not exist
        with transaction.atomic():
            temp = context.pop('tags')
            context['tags'] = [999]
            serializer = MenuItemSerializer(data=new_item_data, context=context)
            self.assertFalse(serializer.is_valid())
            self.assertIn('tags', serializer.errors)
            context['tags'] = temp

    def test_serializer_update(self, mock_gcs_exists):
        """Test updating an existing menu item through serializer"""

        menu_item_id = self.menu_item.id
        updated_data = {
            'title': fake.word(ext_word_list=DISHES_2),
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'description': fake.sentence(),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
            'category': self.category2.id,
            'tags': [self.tag1.id, self.tag2.id],
        }

        context = {
            'tags': updated_data['tags'],
            'category': updated_data['category']
        }

        serializer = MenuItemSerializer(instance=self.menu_item, data=updated_data, context=context)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Check the existing menu item if it was updated correctly
        self.assertEqual(self.menu_item.id, menu_item_id)
        self.assertEqual(self.menu_item.title, updated_data.get('title'))
        self.assertEqual(self.menu_item.price, updated_data.get('price'))
        self.assertEqual(self.menu_item.description, updated_data.get('description'))
        self.assertEqual(self.menu_item.featured, updated_data.get('featured'))
        self.assertEqual(self.menu_item.delivery, updated_data.get('delivery'))
        self.assertEqual(self.menu_item.tags.count(), len(updated_data.get('tags')))
        self.assertEqual(self.menu_item.category, self.category2)
        self.assertIn(self.tag1, self.menu_item.tags.all())
        self.assertIn(self.tag2, self.menu_item.tags.all())

    def test_serializer_partial_update(self, mock_gcs_exists):
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
            'description': self.menu_item.description,
            'featured': partial_update_data['featured'],
            'delivery': partial_update_data['delivery'],
            'category': self.menu_item.category,
            'tags': self.menu_item.tags.all().values_list(flat=True)
        }

        serializer = MenuItemSerializer(instance=self.menu_item, data=partial_update_data, partial=True)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Check the existing menu item if it was updated correctly
        self.assertEqual(self.menu_item.id, expected_updated_data.get('id'))
        self.assertEqual(self.menu_item.title, expected_updated_data.get('title'))
        self.assertEqual(self.menu_item.price, expected_updated_data.get('price'))
        self.assertEqual(self.menu_item.description, expected_updated_data.get('description'))
        self.assertEqual(self.menu_item.featured, expected_updated_data.get('featured'))
        self.assertEqual(self.menu_item.delivery, expected_updated_data.get('delivery'))
        self.assertEqual(self.menu_item.category, expected_updated_data.get('category'))
        self.assertEqual(self.menu_item.tags.count(), len(expected_updated_data.get('tags')))
        self.assertIn(self.tag1, self.menu_item.tags.all())


@patch('storages.backends.gcloud.GoogleCloudStorage.save')
@patch('storages.backends.gcloud.GoogleCloudStorage.exists')
@patch('storages.backends.gcloud.GoogleCloudStorage.url')
@patch('storages.backends.gcloud.GoogleCloudStorage.delete')
class MenuItemImageSerializerTests(TestCase):
    """Test cases for MenuItemImageSerializer"""

    def setUp(self):
        """Set up test data"""

        self.category = Category.objects.create(title="Main Course")

        self.menu_item_data = {
            'title': fake.word(ext_word_list=DISHES_1),
            'price': fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            'description': fake.sentence(),
            'featured': fake.pybool(),
            'delivery': fake.pybool(),
            'category': self.category,
        }

        self.menu_item = MenuItem.objects.create(**self.menu_item_data)

    def test_serializer_contains_expected_fields(self, mock_gcs_delete, mock_gcs_url, mock_gcs_exists, mock_gcs_save):
        """Test that serializer contains only the image field"""

        serializer = MenuItemImageSerializer(instance=self.menu_item)
        data = serializer.data

        expected_fields = ['image']

        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_serializer_upload_image_success(self, mock_gcs_delete, mock_gcs_url, mock_gcs_exists, mock_gcs_save):
        """Test successfully uploading an image for a menu item"""

        # Mock GCS operations
        mock_gcs_save.return_value = f'{settings.MENU_ITEM_MEDIA_ROOT}test_update.png'
        mock_gcs_exists.return_value = True
        mock_gcs_url.return_value = 'https://storage.googleapis.com/bucket/test_update.png'

        # Verify menu item has no image initially
        self.assertFalse(self.menu_item.image)

        # Create an image file
        test_image = create_image_file(name='test_update.png', mode='RGB')

        # Update the menu item with the image
        serializer = MenuItemImageSerializer(instance=self.menu_item, data={'image': test_image})
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())
        updated_item = serializer.save()

        # Verify the image was set
        self.assertIsNotNone(updated_item.image)
        self.assertIn('test_update', updated_item.image.name)

        # Verify GCS save was called
        self.assertTrue(mock_gcs_save.called)

    def test_serializer_replace_existing_image(self, mock_gcs_delete, mock_gcs_url, mock_gcs_exists, mock_gcs_save):
        """Test replacing an existing image with a new one"""

        # Mock GCS operations
        mock_gcs_save.side_effect = [
            f'{settings.MENU_ITEM_MEDIA_ROOT}old_image.png',
            f'{settings.MENU_ITEM_MEDIA_ROOT}new_image.png'
        ]
        mock_gcs_exists.return_value = True
        mock_gcs_url.side_effect = [
            'https://storage.googleapis.com/bucket/old_image.png',
            'https://storage.googleapis.com/bucket/new_image.png'
        ]

        # First, add an image to the menu item
        old_image = create_image_file(name='old_image.png', mode='RGB')
        self.menu_item.image = old_image
        self.menu_item.save()

        # Verify GCS save was called
        self.assertTrue(mock_gcs_save.called)
        mock_gcs_save.reset_mock()

        # Verify old image exists
        self.assertIsNotNone(self.menu_item.image)
        old_image_name = self.menu_item.image.name
        self.assertTrue(self.menu_item.image.storage.exists(old_image_name))

        # Now replace it with a new image
        new_image = create_image_file(name='new_image.png', mode='RGB')
        serializer = MenuItemImageSerializer(instance=self.menu_item, data={'image': new_image})
        self.assertTrue(serializer.is_valid())
        updated_item = serializer.save()

        # Verify the image was updated
        self.assertIsNotNone(updated_item.image)
        self.assertIn('new_image', updated_item.image.name)
        self.assertTrue(self.menu_item.image.storage.exists(updated_item.image.name))

        # Verify GCS save was called
        self.assertTrue(mock_gcs_save.called)

    def test_serializer_validation_missing_image(self, mock_gcs_delete, mock_gcs_url, mock_gcs_exists, mock_gcs_save):
        """Test validation when no image is provided"""

        # Try to update without providing an image
        serializer = MenuItemImageSerializer(instance=self.menu_item, data={})

        # Should be invalid because the image field is required when not partial
        self.assertFalse(serializer.is_valid())
        self.assertIn('image', serializer.errors)

        # Verify GCS save was not called
        self.assertFalse(mock_gcs_save.called)

    def test_serializer_validation_invalid_file_type(self, mock_gcs_delete, mock_gcs_url, mock_gcs_exists, mock_gcs_save):
        """Test validation with an invalid file type"""

        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create a text file instead of an image
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"This is not an image file",
            content_type="text/plain"
        )
        # MenuItemImageSerializer expects an image file, not a text file
        serializer = MenuItemImageSerializer(instance=self.menu_item, data={'image': invalid_file})
        self.assertFalse(serializer.is_valid())
        self.assertIn('image', serializer.errors)

        # Verify GCS save was not called
        self.assertFalse(mock_gcs_save.called)

    def test_serializer_validation_empty_file(self, mock_gcs_delete, mock_gcs_url, mock_gcs_exists, mock_gcs_save):
        """Test validation with an empty file"""

        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create an empty file
        empty_file = SimpleUploadedFile(
            "empty.png",
            b"",
            content_type="image/png"
        )

        # MenuItemImageSerializer expects an image file, not an empty file
        serializer = MenuItemImageSerializer(instance=self.menu_item, data={'image': empty_file})
        self.assertFalse(serializer.is_valid())
        self.assertIn('image', serializer.errors)

    def test_serializer_partial_update(self, mock_gcs_delete, mock_gcs_url, mock_gcs_exists, mock_gcs_save):
        """Test partial update allows optional image"""

        # Mock GCS operations
        mock_gcs_save.return_value = f'{settings.MENU_ITEM_MEDIA_ROOT}partial_update.png'
        mock_gcs_exists.return_value = True
        mock_gcs_url.return_value = 'https://storage.googleapis.com/bucket/partial_update.png'

        # Partial update without an image should be valid
        serializer = MenuItemImageSerializer(instance=self.menu_item, data={}, partial=True)
        self.assertTrue(serializer.is_valid())

        # Partial update with the image should also be valid
        test_image = create_image_file(name='partial_update.png', mode='RGB')
        serializer = MenuItemImageSerializer(instance=self.menu_item, data={'image': test_image}, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_item = serializer.save()

        # Verify the image was set
        self.assertIsNotNone(updated_item.image)

        # Verify GCS save was called
        self.assertTrue(mock_gcs_save.called)

    def test_serializer_multiple_image_formats(self, mock_gcs_delete, mock_gcs_url, mock_gcs_exists, mock_gcs_save):
        """Test updating images with different formats (PNG, JPG, etc.)"""

        # Mock GCS operations
        mock_gcs_save.side_effect = [
            f'{settings.MENU_ITEM_MEDIA_ROOT}test.png',
            f'{settings.MENU_ITEM_MEDIA_ROOT}test.jpg',
            f'{settings.MENU_ITEM_MEDIA_ROOT}test.jpeg',
        ]
        mock_gcs_exists.return_value = True
        mock_gcs_url.side_effect = [
            'https://storage.googleapis.com/bucket/test.png',
            'https://storage.googleapis.com/bucket/test.jpg',
            'https://storage.googleapis.com/bucket/test.jpeg',
        ]

        # Test PNG
        png_image = create_image_file(name='test.png', mode='RGB')
        serializer = MenuItemImageSerializer(instance=self.menu_item, data={'image': png_image})
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Verify GCS save was called and reset mock
        self.assertTrue(mock_gcs_save.called)
        mock_gcs_save.reset_mock()

        # Test JPG
        jpg_image = create_image_file(name='test.jpg', mode='RGB')
        serializer = MenuItemImageSerializer(instance=self.menu_item, data={'image': jpg_image})
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Verify GCS save was called and reset mock
        self.assertTrue(mock_gcs_save.called)
        mock_gcs_save.reset_mock()

        # Test JPEG
        jpeg_image = create_image_file(name='test.jpeg', mode='RGB')
        serializer = MenuItemImageSerializer(instance=self.menu_item, data={'image': jpeg_image})
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Verify GCS save was called
        self.assertTrue(mock_gcs_save.called)

    def test_serializer_image_field_read_only_in_other_fields(self, mock_gcs_delete, mock_gcs_url, mock_gcs_exists, mock_gcs_save):
        """Test that only an image field can be updated, no other fields are exposed"""

        # Mock GCS operations
        mock_gcs_save.return_value = f'{settings.MENU_ITEM_MEDIA_ROOT}test_readonly.png'
        mock_gcs_exists.return_value = True
        mock_gcs_url.return_value = 'https://storage.googleapis.com/bucket/test_readonly.png'

        test_image = create_image_file(name='test_readonly.png', mode='RGB')

        # Try to update an image and other fields (other fields should be ignored)
        data = {
            'image': test_image,
            'title': 'Should be ignored',
            'price': 999.99,
            'description': 'Should be ignored'
        }

        original_title = self.menu_item.title
        original_price = self.menu_item.price
        original_description = self.menu_item.description

        serializer = MenuItemImageSerializer(instance=self.menu_item, data=data)
        self.assertTrue(serializer.is_valid())
        updated_item = serializer.save()

        # Verify that only image was updated, other fields remain unchanged
        self.assertIsNotNone(updated_item.image)
        self.assertEqual(updated_item.title, original_title)
        self.assertEqual(updated_item.price, original_price)
        self.assertEqual(updated_item.description, original_description)
