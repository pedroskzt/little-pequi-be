from django.db import models


# class Category(models.Model):
#     slug = models.SlugField(default="", null=False)
#     title = models.CharField(max_length=255, db_index=True)
#
#     def __str__(self):
#         return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    delivery = models.BooleanField(db_index=True)
    # category = models.ManyToManyField(Category)
    image = models.ImageField(upload_to='img/menu_items/')

    def __str__(self):
        return self.title
