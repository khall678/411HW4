import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from new_idea.db import db
from new_idea.utils.logger import configure_logger
from new_idea.utils.api_utils import get_movie_info
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
configure_logger(logger)

class Movies(db.Model):
    __tablename__ = 'movies'

# Define columns for the table
id = db.Column(db.Integer, primary_key=True)  # Auto-incremented ID
name = db.Column(db.String(100), nullable=False, unique=True)
genre = db.Column(db.String(100), nullable=True)
description = db.Column(db.Text, nullable=True)
year = db.Column(db.String(4), nullable=True)

def __init__(self, name, genre, description, year):
    self.name = name
    self.genre = genre
    self.description = description
    self.year = year

@classmethod
def add_favorite_movie(cls, title):
    """Add a movie as a favorite by fetching details from the IMDB API."""
    movie_details = cls.get_movie_details(title)

    if movie_details:
        new_movie = cls(
            name=title,
            genre=movie_details['genre'],
            description=movie_details['description'],
            year=movie_details['year']
        )
        db.session.add(new_movie)
        db.session.commit()
        return new_movie
    else:
        return None

@classmethod
def get_movie_details(cls, title):
    """Fetch movie details (genre, description, year) from the IMDB API."""
    try:
        # Call the existing get_movie_info function
        movie_info = get_movie_info(title)

        if movie_info and 'data' in movie_info:
            movie_data = movie_info['data']['mainSearch']['edges'][0]['node']['entity']
            genre = movie_data.get('titleType', {}).get('text', 'Unknown')
            description = movie_data.get('originalTitleText', {}).get('text', 'No description available')
            year = movie_data.get('releaseYear', {}).get('year', 'Unknown year')

            return {
                'genre': genre,
                'description': description,
                'year': year
            }
        return None
    except RuntimeError as e:
        logger.error(f"Error fetching movie details: {e}")
        return None

@classmethod
def view_all_favorites(cls):
    """Retrieve all favorite movies with their details."""
    return cls.query.all()

@classmethod
def see_all_favorites(cls):
    """Retrieve a simple list of all favorite movies."""
    return cls.query.all()

@classmethod
def delete_favorite_movie(cls, movie_id):
    """Delete a favorite movie by its ID."""
    movie = cls.query.get(movie_id)
    if movie:
        db.session.delete(movie)
        db.session.commit()
        return movie
    return None

def __repr__(self):
    return f"<Movie {self.name}>"