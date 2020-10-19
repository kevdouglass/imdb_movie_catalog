from django.db import models

# Create your models here.
from django.utils.text import slugify

class Actor(models.Model):
    name = models.CharField(max_length=70, unique=True)
    picture = models.ImageField(blank=True)
    slug = models.SlugField(null=True, unique=True) #cannot be empty, must be unique
    movies = models.ManyToManyField('movie.Movie') # recursive importation

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)