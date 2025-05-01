import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from new_idea.db import db
from new_idea.utils.logger import configure_logger
from new_idea.utils.api_utils import get_movie_info
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy



load_dotenv()

logger = logging.getLogger(__name__)
configure_logger(logger)

class Movies(db.Model):
    __tablename__ = 'movies'
    
    """This model maps to the 'movie' table in the database and stores personal
    and performance-related attributes such as title, year, and actors. Used in a Flask-SQLAlchemy application to
    manage movie data and run simulations"""

    # Define columns for the table
    id = db.Column(db.Integer, primary_key=True)  # Auto-incremented ID
    title = db.Column(db.String(100), nullable=False, unique=True)
    actors = db.Column(db.String(500))
    year = db.Column(db.Integer)

    def __init__(self, title, year, actors):
        """Initialize a new Movie instance with basic attributes.

        Args:
            title (str): The movies's title. Must be unique.
            year (int): The movies's year.
            actors (string): The movies's actors.
            """
        
        self.title = title
        self.year = year
        self.actors = actors

    @classmethod
    def add_favorite_movie(cls, title):
        """Add a movie as a favorite by fetching details from the IMDB API.
        
        This method queries IMDb data using an external utility function, 
        extracts the principal actors and release year, and stores the movie
        in the database if it doesn't exist already
        
        Args:
            title(str): The title of the movie to add
            
        Returns:
            Movies: The newly created movie instance
            
        Raises:
            ValueError: If no movie data is found for the given title
            SQLAlchemyError: If a database error occurs during creation 
        
        """
        logger.info(f"Adding a movie to the list: {title}")

        movie_info = get_movie_info(title).get('data', {}).get('mainSearch', {}).get('edges', [])
        if not movie_info:
            logger.error(f"No movie data found for '{title}'")
            raise ValueError(f"No movie data found for '{title}'")
        
        try:
            actors = []
            for movie in movie_info:
                credits = movie['node']['entity'].get('principalCredits', [])
                for credit in credits:
                    for actor in credit['credits']:
                        actor_name = actor['name']['nameText']['text']
                        actors.append(actor_name)
            
            year = movie_info[0].get('node', {}).get('entity', {}).get('releaseYear', {}).get('year', 'N/A')
            print(f"title: {title} actors: {actors} year: {year}")
            
            new_movie = Movies(
                title=title,
                year=year,
                actors=', '.join(actors)
            )
        
        except ValueError as e:
            logger.warning(f"Validation failed: {e}")
            raise

        # Check if the movie already exists to prevent duplicates
        existing = Movies.query.filter_by(title=title.strip()).first()
        if existing:
            logger.error(f"Movie with name '{title}' already exists.")
            return None  # Return None instead of raising an error

        try:
            db.session.add(new_movie)
            db.session.commit()
            logger.info(f"Movie created successfully: {title}")
            return new_movie
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error during creation: {e}")
            raise


    @classmethod
    def get_movie_details(cls, title):
        """Fetch movie details (title, actors, year) from the database.
        
        Args: 
            title (str): The title of the movie to retrieve
            
        Returns:
            dict: A dictionary containing 'title', 'actors', and 'year'
            
        Raises:
            ValueError: If no movie with the given title exists
            SQLAlchemyError: If a database error occurs during retrieval
            
        """
        # Look for the movie in the database
        logger.info(f"Attempting to retrieve movie details   with title {title}")
        try:
            movie = cls.query.filter_by(title=title.strip()).first()
            if not movie:
                logger.info(f"Movie with title {title} not found.")
                raise ValueError(f"movie with title {title} not found.")
            
            logger.info(f"Successfully retrieved boxer: {movie.title}")
            return {
                'id': movie.id,
                'title': movie.title,
                'actors': movie.actors,
                'year': movie.year
            }
        except ValueError as e:
            logger.info(f"Movie with title {title} not found.")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving movie with title {title}: {e}")
            raise

    

    @classmethod
    def see_all_favorites(cls):
        """Retrieve a simple list of all favorite movie titles.
        
        Returns:
            list: A list of movie titles
            
        Raises:
            SQLAlchemyError: If a database error occurs during retrieval
            
        """
        logger.info(f"Attempting to retrieve all movies from the list")
        try:
            movies = cls.query.all()
            return [movie.title for movie in movies]
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all movie titles: {e}")
            raise

    @classmethod
    def delete_favorite_movie(cls, movie_id):
        """Delete a favorite movie by its ID.
        
        Args:
            movie_id (int): The ID of the movie to delete
            
        Returns:
            dict: A message and the ID of the deleted movie or an 
                  error message if movie wasn't found
                  
        Raises:
            SQLAlchemyError: If a database error occurs during deletion
            
        """
        logger.info(f"Attempting to retrieve movie with ID {movie_id}")
        try:
            movie = cls.query.get(movie_id)
            if movie:
                db.session.delete(movie)
                db.session.commit()
                logger.info(f"Movie '{movie.title}' deleted successfully.")
                return {
                    "message": f"Movie '{movie.title}' deleted successfully.",
                    "deleted_id": movie.id
                }
            else:
                logger.warning(f"No movie found with ID {movie_id}.")
                return {"error": f"No movie found with ID {movie_id}."}
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error deleting movie with ID {movie_id}: {e}")
            raise

    @classmethod
    def clear_all_favorites(cls):
        """Delete all favorite movies from the list.
        
        This method removes all entries from 'movies' table
        
        Returns:
            dict: A message confirming deletion
            
        Raises:
            SQLAlchemyError: If a database error occurs during operation 
            
        """
        logger.info(f"Attempting to retrieve clear all movies from the list")
        try:
            cls.query.delete()  # Deletes all records from the table
            db.session.commit()
            logger.info("All favorite movies have been deleted.")
            return {"message": "All favorite movies have been deleted."}
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"An error occurred while deleting all movies: {e}")
            raise

