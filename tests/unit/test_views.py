from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from api.menu.menu_models import Tag, MenuItem, Category, get_next_display_order_available
from tests.helpers import create_image_file, DISHES_1, DISHES_2

User = get_user_model()
fake = Faker()


class TagViewSetTests(APITestCase):
    """ Test TagViewSet API endpoints."""

    def setUp(self):
        """Set up test data"""

        self.tags = [
            Tag.objects.create(title="Main Course"),
            Tag.objects.create(title="Dessert"),
            Tag.objects.create(title="Appetizer"),
            Tag.objects.create(title="To Share")
        ]

        self.user = User.objects.create_user(
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password=fake.password(length=8)
        )

        self.admin = User.objects.create_user(
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password=fake.password(length=8),
            is_staff=True
        )
        self.list_url = reverse("tag-list")

    def test_create_tag_with_valid_data(self):
        """Test create tags API with valid data"""

        new_tag = {"title": "New Tag"}

        # With user
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, new_tag, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # With admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.list_url, new_tag, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('title', response.data)
        self.assertIn('slug', response.data)
        self.assertEqual(response.data['title'], new_tag['title'])
        self.assertEqual(response.data['slug'], slugify(new_tag['title']))
        self.client.force_authenticate(user=None)

    def test_create_tag_with_invalid_request(self):
        """Test create tags API with an invalid data and missing field"""

        self.client.force_authenticate(user=self.admin)

        # Missing title
        response = self.client.post(self.list_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('required', [errors.code for errors in response.data['title']])

        # Invalid title
        response = self.client.post(self.list_url, {'title': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('blank', [errors.code for errors in response.data['title']])
        self.client.force_authenticate(user=None)

    def test_list_tags(self):
        """Test list tags API"""

        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.tags))

    def test_retrieve_tag(self):
        """Test retrieve tags API"""

        expected_fields = ['id', 'title', 'slug']
        expected_data = {'id': self.tags[0].id,
                         'title': self.tags[0].title,
                         'slug': self.tags[0].slug
                         }

        self.client.force_authenticate(user=None)
        detail_url = reverse("tag-detail", kwargs={'pk': self.tags[0].id})
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(expected_fields))
        self.assertEqual(response.data, expected_data)

    def test_update_tag(self):
        """Test update tags API"""

        datail_url = reverse("tag-detail", kwargs={'pk': self.tags[0].id})

        # As regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.put(datail_url, {'title': 'New Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(datail_url, {'title': 'New Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Title')

    def test_partial_update_category(self):
        """Test partial update tags API"""

        datail_url = reverse("tag-detail", kwargs={"pk": self.tags[0].id})

        # As regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(datail_url, {'title': 'New Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(datail_url, {'title': 'New Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Title')

    def test_destroy_category(self):
        """Test destroy tags API"""

        datail_url = reverse("tag-detail", kwargs={'pk': self.tags[0].id})

        # As regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(datail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(datail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Tag.objects.all()), 3)


class CategoryViewSetTests(APITestCase):
    """ Test CategoryViewSet API endpoints."""

    def setUp(self):
        """Set up test data"""

        self.categories = [
            Category.objects.create(title="Main Course"),
            Category.objects.create(title="Dessert"),
            Category.objects.create(title="Appetizer"),
            Category.objects.create(title="To Share")
        ]

        self.user = User.objects.create_user(
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password=fake.password(length=8)
        )

        self.admin = User.objects.create_user(
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password=fake.password(length=8),
            is_staff=True
        )
        self.list_url = reverse("category-list")

    def test_create_category_with_valid_data(self):
        """Test create categories API with valid data"""

        new_category = {"title": "New Category"}
        next_available_display_order = get_next_display_order_available()

        # With user
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, new_category, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # With admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.list_url, new_category, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('title', response.data)
        self.assertIn('slug', response.data)
        self.assertIn('menu_items', response.data)
        self.assertIn('display_order', response.data)
        self.assertEqual(response.data['title'], new_category['title'])
        self.assertEqual(response.data['slug'], slugify(new_category['title']))
        self.assertEqual(response.data['menu_items'], [])
        self.assertEqual(response.data['display_order'], next_available_display_order)
        self.client.force_authenticate(user=None)

    def test_create_category_with_invalid_request(self):
        """Test create categories API with an invalid data and missing field"""

        self.client.force_authenticate(user=self.admin)

        # Missing title
        response = self.client.post(self.list_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('required', [errors.code for errors in response.data['title']])

        # Invalid title
        response = self.client.post(self.list_url, {'title': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('blank', [errors.code for errors in response.data['title']])
        self.client.force_authenticate(user=None)

    def test_list_categories(self):
        """Test list categories API"""

        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.categories))
        for response_category in response.data:
            self.assertIn('id', response_category)
            self.assertIn('title', response_category)
            self.assertIn('slug', response_category)
            self.assertIn('menu_items', response_category)
            self.assertIn('display_order', response_category)
        self.client.force_authenticate(user=None)

    def test_retrieve_category(self):
        """Test retrieve categories API"""

        expected_fields = ['id', 'title', 'slug', 'menu_items', 'display_order']
        expected_data = {'id': self.categories[0].id,
                         'title': self.categories[0].title,
                         'slug': self.categories[0].slug,
                         'display_order': self.categories[0].display_order,
                         'menu_items': []
                         }

        self.client.force_authenticate(user=None)
        detail_url = reverse("category-detail", kwargs={'pk': self.categories[0].id})
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(expected_fields))
        self.assertEqual(response.data, expected_data)
        self.client.force_authenticate(user=None)

    def test_update_category(self):
        """Test update categories API"""

        datail_url = reverse("category-detail", kwargs={'pk': self.categories[0].id})
        expected_fields = ['id', 'title', 'slug', 'menu_items', 'display_order']
        expected_data = {'id': self.categories[0].id,
                         'title': "New Title",
                         'slug': self.categories[0].slug,
                         'display_order': self.categories[0].display_order,
                         'menu_items': []
                         }

        # As regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.put(datail_url, expected_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(datail_url, expected_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(expected_fields))
        self.assertEqual(response.data, expected_data)
        self.client.force_authenticate(user=None)

    def test_partial_update_category(self):
        """Test partial update categories API"""

        datail_url = reverse("category-detail", kwargs={'pk': self.categories[0].id})

        # As regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(datail_url, {'title': 'New Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(datail_url, {'title': 'New Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Title')
        self.client.force_authenticate(user=None)

    def test_destroy_category(self):
        """Test destroy categories API"""

        datail_url = reverse("category-detail", kwargs={'pk': self.categories[0].id})

        # As regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(datail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(datail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Category.objects.all()), 3)
        self.client.force_authenticate(user=None)

    def test_list_menu_itens_by_category(self):
        """Test list menu items by category API"""

        # Create a menu item and associate it to a category
        tag = Tag.objects.create(title="Vegetarian")

        menu_item_data = {
            "title": fake.word(ext_word_list=DISHES_1),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "description": fake.sentence(),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "category": self.categories[0]
        }

        menu_item = MenuItem.objects.create(**menu_item_data)
        menu_item.tags.add(tag)

        # get API url
        url = reverse("category-menu-items")

        # Call the API as logged off user
        self.client.force_authenticate(user=None)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.categories))
        for category in response.data:
            self.assertIn('id', category)
            self.assertIn('title', category)
            self.assertIn('slug', category)
            self.assertIn('menu_items', category)
            self.assertIn('display_order', category)

            if category['id'] == self.categories[0].id:
                self.assertEqual(len(category['menu_items']), 1)
                self.assertEqual(category['menu_items'][0]['id'], menu_item.id)
                self.assertEqual(category['menu_items'][0]['title'], menu_item.title)
                self.assertEqual(category['menu_items'][0]['price'], str(menu_item.price))
                self.assertEqual(category['menu_items'][0]['description'], menu_item.description)
                self.assertEqual(category['menu_items'][0]['featured'], menu_item.featured)
                self.assertEqual(category['menu_items'][0]['delivery'], menu_item.delivery)
                self.assertEqual(category['menu_items'][0]['tags'], list(menu_item.tags.all().values()))

    # test bulk update
    def test_bulk_update_category(self):
        """Test bulk update categories API"""
        url = reverse("category-bulk")

        updated_data = [
            {
                "id": self.categories[0].id,
                "title": "New Title0",
                "display_order": 1
            },
            {
                "id": self.categories[1].id,
                "title": "New Title1",
                "display_order": 2
            },
            {
                "id": self.categories[2].id,
                "title": "New Title2",
                "display_order": 0
            }
        ]

        # As a regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As an admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for category in response.data:
            self.assertIn('id', category)
            self.assertIn('title', category)
            self.assertIn('slug', category)
            self.assertIn('menu_items', category)
            self.assertIn('display_order', category)

            if category['id'] == updated_data[0]['id']:
                self.assertEqual(category['title'], updated_data[0]['title'])
                self.assertEqual(category['display_order'], updated_data[0]['display_order'])
                self.assertEqual(category['menu_items'], [])
            elif category['id'] == updated_data[1]['id']:
                self.assertEqual(category['title'], updated_data[1]['title'])
                self.assertEqual(category['display_order'], updated_data[1]['display_order'])
                self.assertEqual(category['menu_items'], [])
            elif category['id'] == updated_data[2]['id']:
                self.assertEqual(category['title'], updated_data[2]['title'])
                self.assertEqual(category['display_order'], updated_data[2]['display_order'])
                self.assertEqual(category['menu_items'], [])

        self.client.force_authenticate(user=None)

    def test_partial_bulk_update_category(self):
        """Test partial bulk update categories API"""
        url = reverse("category-bulk")
        updated_data = [
            {
                "id": self.categories[0].id,
                "display_order": 2
            },
            {
                "id": self.categories[1].id,
                "display_order": 0
            },
            {
                "id": self.categories[2].id,
                "display_order": 1
            }
        ]

        # As a regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As an admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for category in response.data:
            self.assertIn('id', category)
            self.assertIn('title', category)
            self.assertIn('slug', category)
            self.assertIn('menu_items', category)
            self.assertIn('display_order', category)

            if category['id'] == updated_data[0]['id']:
                self.assertEqual(category['display_order'], updated_data[0]['display_order'])
            elif category['id'] == updated_data[1]['id']:
                self.assertEqual(category['display_order'], updated_data[1]['display_order'])
            elif category['id'] == updated_data[2]['id']:
                self.assertEqual(category['display_order'], updated_data[2]['display_order'])
        self.client.force_authenticate(user=None)


class MenuItemViewSetTests(APITestCase):
    """ Test MenuItemViewSet API endpoints."""

    def setUp(self):
        """Set up test data"""

        self.category1 = Category.objects.create(title="Main Course")
        self.category2 = Category.objects.create(title="Vegetarian")

        self.tag1 = Tag.objects.create(title="Brazilian")
        self.tag2 = Tag.objects.create(title="Italian")

        self.menu_item_data = {
            "title": fake.word(ext_word_list=DISHES_1),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "description": fake.sentence(),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "category": self.category1
        }

        self.menu_item = MenuItem.objects.create(**self.menu_item_data)
        self.menu_item.tags.add(self.tag1)

        self.user = User.objects.create_user(
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password=fake.password(length=8)
        )

        self.admin = User.objects.create_user(
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password=fake.password(length=8),
            is_staff=True
        )
        self.list_url = reverse("menu-item-list")

    def test_create_menu_item_with_valid_data(self):
        """Test create Menu Item API with valid data"""

        new_menu_item = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "description": fake.sentence(),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "category": self.category2.id,
            "tags": [self.tag2.id]
        }

        tag2_fields = [{
            'id': self.tag2.id,
            'slug': self.tag2.slug,
            'title': self.tag2.title
        }]

        category2_fields = {
            'id': self.category2.id,
            'slug': self.category2.slug,
            'menu_items': [],
            'title': self.category2.title,
            'display_order': self.category2.display_order,
        }

        # With user
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, new_menu_item, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # With admin
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('title', response.data)
        self.assertIn('price', response.data)
        self.assertIn('description', response.data)
        self.assertIn('featured', response.data)
        self.assertIn('delivery', response.data)
        self.assertIn('category', response.data)
        self.assertIn('tags', response.data)

        self.assertEqual(response.data['title'], new_menu_item['title'])
        self.assertEqual(response.data['price'], str(new_menu_item['price']))
        self.assertEqual(response.data['description'], new_menu_item['description'])
        self.assertEqual(response.data['featured'], new_menu_item['featured'])
        self.assertEqual(response.data['delivery'], new_menu_item['delivery'])
        self.assertEqual(response.data['tags'], tag2_fields)
        self.assertEqual(response.data['category'], category2_fields)
        self.client.force_authenticate(user=None)

    def test_create_menu_item_with_missing_required_fields(self):
        """Test create Menu Item API with missing fields"""

        self.client.force_authenticate(user=self.admin)
        new_menu_item = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "description": fake.sentence(),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "category": self.category2.id,
            "tags": [self.tag2.id],
        }

        # Missing Title
        temp = new_menu_item.pop('title')
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('required', [errors.code for errors in response.data['title']])
        new_menu_item['title'] = temp

        # Missing Price
        temp = new_menu_item.pop('price')
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)
        self.assertIn('required', [errors.code for errors in response.data['price']])
        new_menu_item['price'] = temp

        # Missing Featured
        temp = new_menu_item.pop('featured')
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('featured', response.data)
        new_menu_item['featured'] = temp

        # Missing Delivery
        temp = new_menu_item.pop('delivery')
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('delivery', response.data)
        new_menu_item['delivery'] = temp

        # Missing Category
        new_menu_item.pop('category')
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)
        self.assertIn('required', [errors.code for errors in response.data['category']])
        self.client.force_authenticate(user=None)

    def test_create_menu_item_with_invalid_data(self):
        """Test create Menu Item API with invalid data """

        self.client.force_authenticate(user=self.admin)
        new_menu_item = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "description": fake.sentence(),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "category": self.category2.id,
            "tags": [self.tag2.id],
        }

        # Invalid Title
        temp = new_menu_item.pop('title')
        new_menu_item['title'] = ''
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('blank', [errors.code for errors in response.data['title']])
        new_menu_item['title'] = temp

        # Invalid Price
        temp = new_menu_item.pop('price')
        new_menu_item['price'] = 'invalid_price'
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)
        self.assertIn('invalid', [errors.code for errors in response.data['price']])
        new_menu_item['price'] = temp

        # Invalid Description
        temp = new_menu_item.pop('description')
        new_menu_item['description'] = ''
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)
        self.assertIn('blank', [errors.code for errors in response.data['description']])
        new_menu_item['description'] = temp

        # Invalid Featured
        temp = new_menu_item.pop('featured')
        new_menu_item['featured'] = 'invalid_featured'
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('featured', response.data)
        self.assertIn('invalid', [errors.code for errors in response.data['featured']])
        new_menu_item['featured'] = temp

        # Invalid Delivery
        temp = new_menu_item.pop('delivery')
        new_menu_item['delivery'] = 'invalid_delivery'
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('delivery', response.data)
        self.assertIn('invalid', [errors.code for errors in response.data['delivery']])
        new_menu_item['delivery'] = temp

        # Invalid Tag - Non-list tags
        temp = new_menu_item.pop('tags')
        new_menu_item['tags'] = 1
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tags', response.data)
        self.assertIn('invalid', [errors.code for errors in response.data['tags']])
        new_menu_item['tags'] = temp

        # Invalid Tag - Non-numeric tag id
        temp = new_menu_item.pop('tags')
        new_menu_item['tags'] = ['non_numeric_tag_id']
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tags', response.data)
        self.assertIn('invalid', [errors.code for errors in response.data['tags']])
        new_menu_item['tags'] = temp

        # Invalid Tag - Tag Id not found
        temp = new_menu_item.pop('tags')
        new_menu_item['tags'] = [666]
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tags', response.data)
        self.assertIn('invalid', [errors.code for errors in response.data['tags']])
        new_menu_item['tags'] = temp

        # Invalid Category - Non-numeric category id
        temp = new_menu_item.pop('category')
        new_menu_item['category'] = 'non_numeric_category_id'
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)
        self.assertIn('invalid', [errors.code for errors in response.data['category']])
        new_menu_item['category'] = temp

        # Invalid Category - Category id not found
        temp = new_menu_item.pop('category')
        new_menu_item['category'] = 666
        response = self.client.post(self.list_url, new_menu_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)
        self.assertIn('invalid', [errors.code for errors in response.data['category']])

    def test_list_menu_items(self):
        """Test list menu items API"""

        self.client.force_authenticate(user=None)

        new_menu_item = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "description": fake.sentence(),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "category": self.category2,
        }
        new_item = MenuItem.objects.create(**new_menu_item)
        new_item.tags.add(self.tag2)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), MenuItem.objects.count())
        self.client.force_authenticate(user=None)

    def test_retrieve_menu_item(self):
        """Test retrieve Menu Item API"""

        new_menu_item = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "description": fake.sentence(),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "category": self.category2,
        }
        new_item = MenuItem.objects.create(**new_menu_item)
        new_item.tags.add(self.tag2)

        tag1_fields = [{
            'id': self.tag1.id,
            'slug': self.tag1.slug,
            'title': self.tag1.title
        }]

        category1_fields = {
            'id': self.category1.id,
            'slug': self.category1.slug,
            'menu_items': [],
            'title': self.category1.title,
            'display_order': self.category1.display_order,
        }

        expected_fields = ['id', 'title', 'price', 'description', "featured", "delivery", "category", "tags", "image"]
        expected_data = {
            'id': self.menu_item.id,
            "title": self.menu_item.title,
            "price": str(self.menu_item.price),
            "description": self.menu_item.description,
            "featured": self.menu_item.featured,
            "delivery": self.menu_item.delivery,
            "tags": tag1_fields,
            "category": category1_fields,
            "image": None
        }

        self.client.force_authenticate(user=None)
        detail_url = reverse("menu-item-detail", kwargs={"pk": self.menu_item.id})
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(expected_fields))
        self.assertEqual(response.data, expected_data)
        self.client.force_authenticate(user=None)

    def test_update_menu_item(self):
        """Test update Menu Item API"""

        datail_url = reverse("menu-item-detail", kwargs={"pk": self.menu_item.id})

        tag2_fields = [{
            'id': self.tag2.id,
            'slug': self.tag2.slug,
            'title': self.tag2.title
        }]

        category2_fields = {
            'id': self.category2.id,
            'slug': self.category2.slug,
            'menu_items': [],
            'title': self.category2.title,
            'display_order': self.category2.display_order,
        }

        updated_data = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "description": fake.sentence(),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "category": self.category2.id,
            "tags": [self.tag2.id]
        }

        # As regular user
        self.client.force_authenticate(user=self.user)

        response = self.client.put(datail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As admin
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(datail_url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], updated_data['title'])
        self.assertEqual(response.data['price'], str(updated_data['price']))
        self.assertEqual(response.data['description'], updated_data['description'])
        self.assertEqual(response.data['featured'], updated_data['featured'])
        self.assertEqual(response.data['delivery'], updated_data['delivery'])
        self.assertEqual(response.data['tags'], tag2_fields),
        self.assertEqual(response.data['category'], category2_fields)
        self.client.force_authenticate(user=None)

    def test_partial_update_menu_item(self):
        """Test partial update Menu Item API"""

        datail_url = reverse("menu-item-detail", kwargs={"pk": self.menu_item.id})

        updated_data = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
        }

        tag1_fields = [{
            'id': self.tag1.id,
            'slug': self.tag1.slug,
            'title': self.tag1.title
        }]

        category1_fields = {
            'id': self.category1.id,
            'slug': self.category1.slug,
            'menu_items': [],
            'title': self.category1.title,
            'display_order': self.category1.display_order,
        }

        # As regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(datail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(datail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], updated_data['title'])
        self.assertEqual(response.data['price'], str(updated_data['price']))
        self.assertEqual(response.data['description'], self.menu_item.description)
        self.assertEqual(response.data['featured'], updated_data['featured'])
        self.assertEqual(response.data['delivery'], updated_data['delivery'])
        self.assertEqual(response.data['tags'], tag1_fields),
        self.assertEqual(response.data['category'], category1_fields)
        self.client.force_authenticate(user=None)

    @patch('core.BlobManager.BlobHandler.BlobHandler.BlobHandler.delete_blob')
    @patch('storages.backends.gcloud.GoogleCloudStorage.exists')
    @patch('storages.backends.gcloud.GoogleCloudStorage.save')
    def test_update_image(self, mock_gcs_save, mock_gcs_exists, mock_delete_blob, ):
        """Test update image API"""
        update_image_url = reverse("menu-item-image", kwargs={"pk": self.menu_item.id})

        # Mock the GCS save method to return a fake path
        image_name = f'{settings.MENU_ITEM_MEDIA_ROOT}test_gcs_image.png'
        mock_gcs_save.return_value = image_name
        mock_gcs_save.side_effect = lambda name, content, max_length=None: name
        mock_gcs_exists.return_value = True

        # Mock the delete_blob method to simulate successful deletion
        mock_delete_blob.return_value = None

        # Create the image
        initial_image = create_image_file(name='test_gcs_image.png', mode='L')

        # Add the image to the menu item
        self.menu_item.image = initial_image
        self.menu_item.save()

        old_image_name = self.menu_item.image.name
        old_image_url = self.menu_item.image.url

        # Check if the image exists on the menu item object
        self.assertTrue(self.menu_item.image.storage.exists(old_image_name))

        # As regular user
        self.client.force_authenticate(user=self.user)
        new_image = create_image_file(name='new_gcs_image.png', mode='L')
        response = self.client.post(update_image_url, {'image': new_image}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)
        # Verify that delete_blob wasn't called with the correct image name
        mock_delete_blob.assert_not_called()

        # As admin
        self.client.force_authenticate(user=self.admin)
        new_image = create_image_file(name='new_gcs_image.png', mode='L')
        response = self.client.post(update_image_url, {'image': new_image}, format='multipart')
        self.menu_item.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the image still exists on the menu item object
        self.assertTrue(self.menu_item.image.storage.exists(self.menu_item.image.name))

        # Check if the image was changed
        self.assertEqual(response.data['image'], self.menu_item.image.url)
        self.assertNotEqual(response.data['image'], old_image_url)


        self.client.force_authenticate(user=None)

        # Verify that delete_blob was called with the correct image name
        mock_delete_blob.assert_called_once_with(old_image_name)


    @patch('core.BlobManager.BlobHandler.BlobHandler.BlobHandler.delete_blob')
    @patch('storages.backends.gcloud.GoogleCloudStorage.exists')
    @patch('storages.backends.gcloud.GoogleCloudStorage.save')
    def test_destroy_menu_item(self, mock_gcs_save, mock_gcs_exists, mock_delete_blob,):
        """Test destroy Menu Item API"""

        datail_url = reverse("menu-item-detail", kwargs={"pk": self.menu_item.id})


        # Mock the GCS save method to return a fake path
        image_name = f'{settings.MENU_ITEM_MEDIA_ROOT}test_gcs_image.png'
        mock_gcs_save.return_value = image_name
        mock_gcs_save.side_effect = lambda name, content, max_length=None: name
        mock_gcs_exists.return_value = True

        # Mock the delete_blob method to simulate successful deletion
        mock_delete_blob.return_value = None

        # Create a menu item with an image
        test_image = create_image_file(name='test_gcs_image.png', mode='L')

        # Add the image to the menu item
        self.menu_item.image = test_image
        self.menu_item.save()

        old_image_name = self.menu_item.image.name

        # Check if the image exists on the menu item object
        image_exists = self.menu_item.image.storage.exists(old_image_name)
        self.assertTrue(image_exists)

        # As regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(datail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(datail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(MenuItem.objects.all()), 0)
        self.client.force_authenticate(user=None)

        # Verify that delete_blob was called with the correct image name
        mock_delete_blob.assert_called_once_with(old_image_name)
