from django.db import models

# Create your models here.
from django.utils.text import slugify
from actor.models import Actor

import requests
from io import BytesIO
from django.core import files
from django.urls import reverse


class Genre(models.Model):
    title = models.CharField(max_length=25)
    slug = models.SlugField(null=False, unique=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # just incase we get empty space in API request, eliminate it and replace with no spaces
            self.title.replace(" ", "") 
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
    
    
class Rating(models.Model):
    source = models.CharField(max_length=50)
    rating = models.CharField(max_length=10)
    
    def __str__(self):
        return self.source
    
    

class Movie(models.Model):
    Title = models.CharField(max_length=200)
    Year = models.CharField(max_length=25, blank=True)
    Rated = models.CharField(max_length=25, blank=True)
    Released = models.CharField(max_length=25, blank=True)
    Runtime = models.CharField(max_length=25, blank=True)
    Genre = models.ManyToManyField(Genre, blank=True)
    Director = models.CharField(max_length=100, blank=True)
    Writer = models.CharField(max_length=300, blank=True)
    Actors = models.ManyToManyField(Actor, blank=True)
    Plot = models.CharField(max_length=900, blank=True)
    Language = models.CharField(max_length=300, blank=True)
    Country = models.CharField(max_length=100, blank=True)
    Awards = models.CharField(max_length=250, blank=True)
    Poster = models.ImageField(upload_to='movies', blank=True)
    Poster_url = models.URLField(blank=True)
    Ratings = models.ManyToManyField(Rating, blank=True)
    Metascore = models.CharField(max_length=5, blank=True)
    imdbRating = models.CharField(max_length=5, blank=True)  
    imdbVotes = models.CharField(max_length=100, blank=True)
    # imdb unique ID when looking up movies on their website.
    imdbID = models.CharField(max_length=100, blank=True)
    Type = models.CharField(max_length=10, blank=True)
    DVD = models.CharField(max_length=25, blank=True)
    BoxOffice = models.CharField(max_length=25, blank=True)
    Production = models.CharField(max_length=100, blank=True)
    Website = models.CharField(max_length=150, blank=True)
    totalSeasons = models.CharField(max_length=3, blank=True)
 
    def __str__(self):
        return self.Title
    
    def save(self, *args, **kwargs):
        '''
        POSTER_URL
        ----------
            > overide the save method. Ssave the URL to the poster_url incoming from the API endpoint..
            > picture we get from the URL and save to our database/ server so we get the photo/poster
            > if our poster is empty and if our poster_url is NOT empy.. (if we dont have a poster but we have a poster URL... there is a problem LOL)
                    > use requests.get to create a request for the Poster_url
                    
            BytesIO()
            ---------
            >   Get url and turn into bytes..
            > write the requests content in bytes
            > flush/ delete the temp file it creates
                >   Create a file for our poster_url
                >   Save() comes from models.ImageField() where we are going to import files from django.core so we can work with files
                    >   save=False because we are saving locally. If it is not there, it will return duplicate files for the img url
            
        '''
        if self.Poster == '' and self.Poster_url != '':
            resp = requests.get(self.Poster_url)
            pb = BytesIO()
            pb.write(resp.content)
            pb.flush()
            file_name = self.Poster_url.split("/")[-1]
            self.Poster.save(file_name, files.File(pb), save=False)
        
        return super().save(*args, **kwargs)
    
    
RATE_CHOICES = [
	(1, '1 - Trash'),
	(2, '2 - Horrible'),
	(3, '3 - Terrible'),
	(4, '4 - Bad'),
	(5, '5 - OK'),
	(6, '6 - Watchable'),
	(7, '7 - Good'),
	(8, '8 - Very Good'),
	(9, '9 - Perfect'),
	(10, '10 - Master Piece'), 
        
        
]




class Review(models.Model):
	# user = models.ForeignKey(User, on_delete=models.CASCADE)
	movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	text = models.TextField(max_length=3000, blank=True)
	rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES)
	likes = models.PositiveIntegerField(default=0)
	unlikes = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.user.username

class Likes(models.Model):
	# user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_like')
	type_like = models.PositiveSmallIntegerField()
	review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_like')
    
    
    