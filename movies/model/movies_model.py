import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from new_idea.db import db
from new_idea.utils.logger import configure_logger
from new_idea.utils.api_utils import get_random

logger = logging.getLogger(__name__)
configure_logger(logger)

class Movie(db.Model):
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
def add_favorite_movie(cls, name, genre, description, year):
    """Set a favorite movie by adding it to the database."""
    new_movie = cls(name=name, genre=genre, description=description, year=year)
    db.session.add(new_movie)
    db.session.commit()
    return new_movie

@classmethod
def get_favorite_movies(cls, movie_id):
    """Retrieve details for a favorite movie by its ID."""
    return cls.query.get(movie_id)

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