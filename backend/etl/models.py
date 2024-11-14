from io import BytesIO
from PIL import Image
from django.contrib.postgres.fields import ArrayField
from django.core.files import File
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField() #address version of the name

    #options for the model
    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}/'


class Backlog(models.Model):
    link = models.TextField()
    attempts = models.IntegerField(default=0)


class Perfume(models.Model):
    link = models.TextField()
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    rel_year = models.IntegerField()
    rel_decade = models.IntegerField()
    notes = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
    )
    chart_categories = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
    )
    chart_numbers = ArrayField(
        models.IntegerField(),
        blank=True,
        default=list,
    )
    scent = models.FloatField()
    longevity = models.FloatField()
    sillage = models.FloatField()
    bottle = models.FloatField()
    value_for_money = models.FloatField()

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank = True, null = True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='uploads/', blank = True, null = True)
    thumbnail = models.ImageField(upload_to='uploads/', blank =True, null = True)
    date_added = models.DateTimeField(auto_now_add=True)

    """
    The Meta class in Django models is a way to define metadata about the model. 
    It allows you to configure options for how the model behaves, 
    interacts with the database, and is presented in the admin interface.
    """
    class Meta:
        ordering = ('-date_added',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.category.slug}/{self.slug}/'

    def get_image(self):
        # if you have image in the field
        if self.image:
            return 'http://127.0.0.1:8000' + self.image.url
        return ''

    def get_thumbnail(self):
        # if you have thumbnail in the field
        if self.thumbnail:
            return 'http://127.0.0.1:8000' + self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                # save in the database
                self.save()

                return 'http://127.0.0.1:8000' + self.thumbnail.url
            else:
                return ''

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img = img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail
