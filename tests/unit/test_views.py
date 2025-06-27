import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from api.menu import Category, MenuItem
from tests.helpers import create_image_file, DISHES_1, DISHES_2

User = get_user_model()
fake = Faker()


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
        """Test create category API with valid data"""

        new_category = {"title": "New Category"}

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
        self.assertEqual(response.data['title'], new_category['title'])
        self.assertEqual(response.data['slug'], slugify(new_category['title']))
        self.client.force_authenticate(user=None)

    def test_create_category_with_invalid_request(self):
        """Test create category API with an invalid data and missing field"""

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

    def test_retrieve_category(self):
        """Test retrieve category API"""

        expected_fields = ['id', 'title', 'slug']
        expected_data = {'id': self.categories[0].id,
                         'title': self.categories[0].title,
                         'slug': self.categories[0].slug
                         }

        self.client.force_authenticate(user=None)
        detail_url = reverse("category-detail", kwargs={"slug": self.categories[0].slug})
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(expected_fields))
        self.assertEqual(response.data, expected_data)

    def test_update_category(self):
        """Test update category API"""

        datail_url = reverse("category-detail", kwargs={"slug": self.categories[0].slug})

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
        """Test partial update category API"""

        datail_url = reverse("category-detail", kwargs={"slug": self.categories[0].slug})

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
        """Test destroy category API"""

        datail_url = reverse("category-detail", kwargs={"slug": self.categories[0].slug})

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


class MenuItemViewSetTests(APITestCase):
    """ Test MenuItemViewSet API endpoints."""

    def setUp(self):
        """Set up test data"""

        self.category1 = Category.objects.create(title="Main Course")
        self.category2 = Category.objects.create(title="Vegetarian")

        self.menu_item_data = {
            "title": fake.word(ext_word_list=DISHES_1),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "image": create_image_file(name='test_image.png', mode='L')
        }
        self.menu_item = MenuItem.objects.create(**self.menu_item_data)
        self.menu_item.category.add(self.category1)

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
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "category": [self.category2.id],
            "image": create_image_file(name='test_image.png', mode='L')
        }

        # With user
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, new_menu_item, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # With admin
        self.client.force_authenticate(user=self.admin)

        new_menu_item['image'] = create_image_file(name='test_new_image.png', mode='L')
        response = self.client.post(self.list_url, new_menu_item, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('title', response.data)
        self.assertIn('price', response.data)
        self.assertIn('featured', response.data)
        self.assertIn('delivery', response.data)
        self.assertIn('image', response.data)
        self.assertIn('category', response.data)

        self.assertEqual(response.data['title'], new_menu_item['title'])
        self.assertEqual(response.data['price'], str(new_menu_item['price']))
        self.assertEqual(response.data['featured'], new_menu_item['featured'])
        self.assertEqual(response.data['delivery'], new_menu_item['delivery'])
        self.assertEqual(response.data['category'], new_menu_item['category'])
        self.assertIn(new_menu_item['image'].name, response.data['image'])
        os.remove(settings.MEDIA_ROOT / f'{settings.MENU_ITEM_MEDIA_ROOT}{new_menu_item['image'].name}')

    def test_create_menu_item_with_missing_required_fields(self):
        """Test create Menu Item API with missing fields"""

        self.client.force_authenticate(user=self.admin)
        new_menu_item = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "category": [self.category2.id],
            "image": create_image_file(name='test_image.png', mode='L')
        }

        # Missing Title
        temp = new_menu_item.pop('title')
        response = self.client.post(self.list_url, new_menu_item, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('required', [errors.code for errors in response.data['title']])
        new_menu_item['title'] = temp

        # Missing Price
        temp = new_menu_item.pop('price')
        new_menu_item['image'] = create_image_file(name='test_image.png', mode='L')
        response = self.client.post(self.list_url, new_menu_item, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)
        self.assertIn('required', [errors.code for errors in response.data['price']])
        new_menu_item['price'] = temp

        # Missing Featured
        temp = new_menu_item.pop('featured')
        new_menu_item['image'] = create_image_file(name='test_image.png', mode='L')
        response = self.client.post(self.list_url, new_menu_item, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('featured', response.data)
        new_menu_item['featured'] = temp

        # Missing Delivery
        temp = new_menu_item.pop('delivery')
        new_menu_item['image'] = create_image_file(name='test_image.png', mode='L')
        response = self.client.post(self.list_url, new_menu_item, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('delivery', response.data)
        new_menu_item['delivery'] = temp

        # Missing Image
        new_menu_item.pop('image')
        response = self.client.post(self.list_url, new_menu_item, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', response.data)
        self.assertIn('required', [errors.code for errors in response.data['image']])

    def test_create_menu_item_with_invalid_data(self):
        """Test create Menu Item API with invalid data """

        self.client.force_authenticate(user=self.admin)
        new_menu_item = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "category": [self.category2.id],
            "image": create_image_file(name='test_image.png', mode='L')
        }

        # Invalid Title
        temp = new_menu_item.pop('title')
        new_menu_item['title'] = ''
        response = self.client.post(self.list_url, new_menu_item, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('blank', [errors.code for errors in response.data['title']])
        new_menu_item['title'] = temp

        # Invalid Price
        temp = new_menu_item.pop('price')
        new_menu_item['image'] = create_image_file(name='test_image.png', mode='L')
        new_menu_item['price'] = 'invalid_price'
        response = self.client.post(self.list_url, new_menu_item, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)
        self.assertIn('invalid', [errors.code for errors in response.data['price']])
        new_menu_item['price'] = temp

        # Invalid Featured
        temp = new_menu_item.pop('featured')
        new_menu_item['image'] = create_image_file(name='test_image.png', mode='L')
        new_menu_item['featured'] = 'invalid_featured'
        response = self.client.post(self.list_url, new_menu_item, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('featured', response.data)
        self.assertIn('invalid', [errors.code for errors in response.data['featured']])
        new_menu_item['featured'] = temp

        # Invalid Delivery
        temp = new_menu_item.pop('delivery')
        new_menu_item['image'] = create_image_file(name='test_image.png', mode='L')
        new_menu_item['delivery'] = 'invalid_delivery'
        response = self.client.post(self.list_url, new_menu_item, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('delivery', response.data)
        self.assertIn('invalid', [errors.code for errors in response.data['delivery']])
        new_menu_item['delivery'] = temp

        # Invalid Image
        new_menu_item['image'] = 'invalid_image'
        response = self.client.post(self.list_url, new_menu_item, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', response.data)
        self.assertIn('invalid', [errors.code for errors in response.data['image']])

        # Empty Image
        new_menu_item['image'] = create_image_file(name='test_image.png', empty_image=True)
        response = self.client.post(self.list_url, new_menu_item, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', response.data)
        self.assertIn('empty', [errors.code for errors in response.data['image']])

    def test_list_meun_items(self):
        """Test list menu items API"""

        self.client.force_authenticate(user=None)

        new_menu_item = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "image": create_image_file(name='test_image.png', mode='L')
        }
        new_item = MenuItem.objects.create(**new_menu_item)
        new_item.category.add(self.category2)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), MenuItem.objects.count())

    def test_retrieve_menu_item(self):
        """Test retrieve Menu Item API"""

        new_menu_item = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "image": create_image_file(name='test_image.png', mode='L')
        }
        new_item = MenuItem.objects.create(**new_menu_item)
        new_item.category.add(self.category2)

        expected_fields = ['id', 'title', 'price', "featured", "delivery", "image", "category"]
        expected_data = {
            'id': self.menu_item.id,
            "title": self.menu_item.title,
            "price": str(self.menu_item.price),
            "featured": self.menu_item.featured,
            "delivery": self.menu_item.delivery,
            "category": [self.category1.id],
            "image": None
        }

        self.client.force_authenticate(user=None)
        detail_url = reverse("menu-item-detail", kwargs={"pk": self.menu_item.id})
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), set(expected_fields))
        response_data = response.data
        response_image = response_data.pop('image')
        expected_data.pop('image')

        self.assertEqual(response_data, expected_data)
        self.assertIn(self.menu_item.image.name, response_image)

    def test_update_menu_item(self):
        """Test update Menu Item API"""

        datail_url = reverse("menu-item-detail", kwargs={"pk": self.menu_item.id})

        updated_data = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
            "category": [self.category2.id],
            "image": create_image_file(name='test_image.png', mode='L')
        }

        # As regular user
        self.client.force_authenticate(user=self.user)

        response = self.client.put(datail_url, updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As admin
        self.client.force_authenticate(user=self.admin)

        updated_data['image'] = create_image_file(name='test_new_image.png', mode='L')
        response = self.client.put(datail_url, updated_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], updated_data['title'])
        self.assertEqual(response.data['price'], str(updated_data['price']))
        self.assertEqual(response.data['featured'], updated_data['featured'])
        self.assertEqual(response.data['delivery'], updated_data['delivery'])
        self.assertEqual(response.data['category'], updated_data['category'])
        self.assertIn(updated_data['image'].name, response.data['image'])
        os.remove(settings.MEDIA_ROOT / f'{settings.MENU_ITEM_MEDIA_ROOT}{updated_data['image'].name}')

    def test_partial_update_menu_item(self):
        """Test partial update Menu Item API"""

        datail_url = reverse("menu-item-detail", kwargs={"pk": self.menu_item.id})

        updated_data = {
            "title": fake.word(ext_word_list=DISHES_2),
            "price": fake.pydecimal(left_digits=2, right_digits=2, positive=True),
            "featured": fake.boolean(),
            "delivery": fake.boolean(),
        }

        # As regular user
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(datail_url, updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('permission_denied', response.data['detail'].code)
        self.client.force_authenticate(user=None)

        # As admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(datail_url, updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], updated_data['title'])
        self.assertEqual(response.data['price'], str(updated_data['price']))
        self.assertEqual(response.data['featured'], updated_data['featured'])
        self.assertEqual(response.data['delivery'], updated_data['delivery'])

    def test_destroy_menu_item(self):
        """Test destroy Menu Item API"""

        datail_url = reverse("menu-item-detail", kwargs={"pk": self.menu_item.id})

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
