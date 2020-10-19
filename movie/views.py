from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Avg

from movie.models import Movie, Genre, Rating, Review
from actor.models import Actor
# from authy.models import Profile
from django.contrib.auth.models import User


# from movie.forms import RateForm

import requests

# api key: 1a2f4145
# http://www.omdbapi.com/?i=tt3896198&apikey=1a2f4145
# Create your views here.

def index(request):
    '''
    >   Return index.html 
    '''
    query = request.GET.get('searchbox')

    # if we have a search query, build the URL
        # query would be the movie title in this case 'Batman'
    if query:
        # print('DEBUG: Query is TRUE..........')
        url = 'http://www.omdbapi.com/?' + 'apikey=1a2f4145&s=' + query
        #url = 'http://www.omdbapi.com/?apikey=1a2f4145&s=' + query
        #   save response from API, pass the URL resp. from server
        response = requests.get(url)
        # print(f'RESPONSE: .......{response}')
        movie_data = response.json()
        # print(f'\n\nMOVIE_DATA: .......{movie_data}')

        
        
        # Store api request params in context dictionary
        context = {
            'query': query,
            'movie_data': movie_data,
            # default value needs to be set for page_number
            'page_number': 1,
        }
        
        #   Load the template "LOADER"
        template = loader.get_template('search_results.html')
        
        return HttpResponse(template.render(context, request))
    
    return render(request, 'index.html')

def pagination(request, query, page_number):
    '''
    >   search through multiple page from API, query pagination in API
    '''
    url = 'http://www.omdbapi.com/?' + 'apikey=1a2f4145&s=' + query + '&page=' + str(page_number)
    #url = 'http://www.omdbapi.com/?apikey=1a2f4145&s=' + query + '&page=' + str(page_number)
    response = requests.get(url)
    movie_data= response.json()
    # change page we want to 
    page_number = int(page_number) + 1
    # Store api request params in context dictionary
    context = {
        'query': query,
        'movie_data': movie_data,
        'page_number': page_number,
    }
    
    template = loader.get_template('search_results.html')
    
    return HttpResponse(template.render(context, request))



def movieDetails(request, imdb_id):
    '''
    > check if movie is in database first
    > filter the movie model if it is (by imdb_id)
    > save movie-data to rating_obs[], genre_obs[], and actor_objs[]
    > Create slug for user to search by Genre
    '''
    if Movie.objects.filter(imdbID=imdb_id).exists():
        movie_data = Movie.objects.get(imdbID=imdb_id)
        our_db = True
    else:
        url = '' + imdb_id
        response = requests.get(url)
        movie_data = response.json()
        
        #   Inject data to our database below
        rating_objs = []
        genre_objs = []
        actor_objs = []
        
        #   Create List For the actors
            # get 'actors' field from db Model
        actor_list = [x.strip() for x in movie_data['Actors'].split(',')]
        
        for actor in actor_list:
            a, created = Actor.objects.get_or_create(name=actor)
            actor_objs.append(a) # append the newly created actor
            
        # For the Genre and Categories
        genre_list = list(movie_data['Genre'].replace(' ', '').split(','))
        
        for genre in genre_list:
            # to be able to search with SLUG
            genre_slug = slugify(genre)
            g, created = Genre.objects.get_or_create(title=genre, slug=genre_slug)
            genre_objs.append(g)    #   Append the Genre
            
        #   For the Ratings (which is a list in the API)
        for rate in movie_data['Ratings']:
            r, created = Rating.objects.get_or_create(source=rate['Source'], rating=rate['Value'])  #   Get list obj by name-label
            rating_objs.append(r)   #   Append the ratings
            
        if movie_data['Type'] == 'movie':
            # then create with movie fields
            #  LABELS: Title Year Rated  Released Runtime Genre Director Writer Actors Plot .. ..
            #       >> Language Country Awards Poster Poster_url Ratings Metascore imdbRating imdbVotes imdbID Type DVD BoxOffice Production Website totalSeasons
            m, created = Movie.objects.get_or_create(''' put MOVIE-data here''',
                                                     Title=movie_data['Title'],
                                                     Year=movie_data['Year'],
                                                     Rated=movie_data['Rated'],
                                                     Released=movie_data['Released'],
                                                     Runtime=movie_data['Runtime'],
                                                     Genre=movie_data['Genre'],
                                                     Director=movie_data['Director'],
                                                     Writer=movie_data['Writer'],
                                                     Actors=movie_data['Actors'],
                                                     Plot=movie_data['Plot'],
                                                     Language=movie_data['Language'],
                                                     Country=movie_data['Country'],
                                                     Awards=movie_data['Awards'],
                                                    #  Poster=movie_data['Poster'],
                                                     Poster_url=movie_data['Poster'],
                                                     Ratings=movie_data['Ratings'],
                                                     Metascore=movie_data['Metascore'],
                                                     imdbRating=movie_data['imdbRating'],
                                                     imdbVotes=movie_data['imdbVotes'],
                                                     imdbID=movie_data['imdbID'],
                                                     Type=movie_data['Type'],
                                                     DVD=movie_data['DVD'],
                                                     BoxOffice=movie_data['BoxOffice'],
                                                     Production=movie_data['Production'],
                                                     Website=movie_data['Website'],)
            m.Genre.set(genre_objs)
            m.Actors.set(actor_objs)
            m.Ratings.set(rating_objs)
        else:
            
            m, created = Movie.objects.get_or_create(''' else it is a TV-series''',
                                                     Title=movie_data['Title'],
                                                     Year=movie_data['Year'],
                                                     Rated=movie_data['Rated'],
                                                     Released=movie_data['Released'],
                                                     Runtime=movie_data['Runtime'],
                                                     Genre=movie_data['Genre'],
                                                     Director=movie_data['Director'],
                                                     Writer=movie_data['Writer'],
                                                     Actors=movie_data['Actors'],
                                                     Plot=movie_data['Plot'],
                                                     Language=movie_data['Language'],
                                                     Country=movie_data['Country'],
                                                     Awards=movie_data['Awards'],
                                                    #  Poster=movie_data['Poster'],
                                                     Poster_url=movie_data['Poster'],
                                                     Ratings=movie_data['Ratings'],
                                                     Metascore=movie_data['Metascore'],
                                                     imdbRating=movie_data['imdbRating'],
                                                     imdbVotes=movie_data['imdbVotes'],
                                                     imdbID=movie_data['imdbID'],
                                                     Type=movie_data['Type'],
                                                     totalSeasons=movie_data['totalSeasons'],)
            m.Genre.set(genre_objs)
            m.Actors.set(actor_objs)
            m.Ratings.set(rating_objs)
            
        #   Actors
            #   each class of Actor objects have a Movie attribute.. save the movie they were in to the Actor.Movie attr
        for actor in actor_objs:
            actor.movies.add(m) #   Add the movie object to the actor
            actor.save()
            
            
        # Save the move
        m.save()
        our_db = False  #   Specify this data is not coming from our DB
        
    context = {
        'movie_data': movie_data,
        'our_db': our_db,
    } 
    
    template = loader.get_template('movie_details.html')
    
    return HttpResponse(template.render(context, request))
        