import os

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True, db_index=True)
    slug = models.SlugField(max_length=60, unique=True, blank=False)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

def get_next_display_order_available():
    categories = Category.objects.all().order_by('display_order').values_list('display_order', flat=True)
    if categories.exists():
        categories = list(categories)
        next_available = sum(range(categories[0], categories[-1] + 1)) - sum(categories)
        if next_available == 0 and 0 in categories:
            return categories[-1] + 1
        return next_available
    return 0

class Category(models.Model):
    title = models.CharField(max_length=50, unique=True, db_index=True)
    slug = models.SlugField(max_length=60, unique=True, blank=False)
    display_order = models.PositiveSmallIntegerField(default=get_next_display_order_available)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)


def custom_filename(instance, filename):
    extension = filename.split('.')[-1]
    name = filename.replace(f'.{extension}', '')
    return os.path.join(settings.MENU_ITEM_MEDIA_ROOT,
                        f'{name}-{instance.id}-{timezone.now().strftime("%Y%m%d%H%M%S")}.{extension}')


class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    featured = models.BooleanField(db_index=True, default=True)
    delivery = models.BooleanField(db_index=True, default=False)
    tags = models.ManyToManyField(Tag, blank=True, db_index=True, related_name='menu_items')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='menu_items')
    image = models.ImageField(upload_to=custom_filename, blank=True, null=True)

    # date_created = models.DateTimeField(auto_now_add=True)
    # date_updated = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
