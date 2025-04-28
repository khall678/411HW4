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
    title = db.Column(db.String(100), nullable=False, unique=True)
    actors = db.Column(db.String(100), nullable=True)
    year = db.Column(db.String(4), nullable=True)

    def __init__(self, title, year, actors):
        self.title = title
        self.year = year
        self.actors = actors

    @classmethod
    def add_favorite_movie(cls, title):
        """Add a movie as a favorite by fetching details from the IMDB API."""
        logger.info(f"Adding a movie to the list: {title}")

        movie_info = get_movie_info(title).get('data', {}).get('mainSearch',{}).get('edges', [])
        if not movie_info:
            logger.error(f"No movie data found for '{title}'")
            raise ValueError(f"No movie data found for '{title}'")
        
        try:
                actors =[]
                for movie in movie_info:
                        credits = movie['node']['entity'].get('principalCredits',[])
                        for credits in credits:
                            for actor in credits['credits']:
                                actor_name = actor['name']['nameText']['text']
                                actors.append(actor_name)
                
                year=movie_info[0].get('node', {}).get('entity', {}).get('releaseYear',{}).get('year', 'N/A')
                print(f"title: {title} actors: {actors} year: {year}")
                                                                                            
                new_movie = Movies(
                    title=title,
                    year=year,
                    actors=actors,
                )
        
        except ValueError as e:
            logger.warning(f"Validation failed: {e}")
            raise

        try:
            #check for exisitng movie with the same name
            existing = Movies.query.filter_by(title=title.strip()).first()
            if existing:
                logger.error(f"Movie with name '{title}' already exists.")
                raise IntegrityError(f"Movie with name '{title}' already exists.", params=None, orig=None)
            
            db.session.add(new_movie)
            db.session.commit()
            logger.info(f"Movie created successfully: {title}")
            return new_movie
        except IntegrityError:
            db.session.rollback()
            logger.error(f"Movie with name '{title}' already exists.")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error during creation: {e}") 
            db.session.rollback()
            raise

    @classmethod
    def get_movie_details(cls, title):
        """Fetch movie details (title, actors, year) from the database."""
        # Look for the movie in the database
        movie = cls.query.filter_by(title=title.strip()).first()
        
        if movie:
            return {
                'title': movie.title,
                'actors': movie.actors,
                'year': movie.year
            }
        else:
            logger.error(f"Movie '{title}' not found in favorites.")
            return None
    

    @classmethod
    def see_all_favorites(cls):
        """Retrieve a simple list of all favorite movie titles."""
        movies = cls.query.all()
        return [movie.title for movie in movies]

    @classmethod
    def delete_favorite_movie(cls, movie_id):
        """Delete a favorite movie by its ID."""
        movie = cls.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return {
                "message": f"Movie '{movie.title}' deleted successfully.",
                "deleted_id": movie.id
            }
        else:
            return {
                "error": f"No movie found with ID {movie_id}."
            }
    @classmethod
    def clear_all_favorites(cls):
        """Delete all favorite movies from the list."""
        try:
            cls.query.delete()  # Deletes all records from the table
            db.session.commit()
            return {"message": "All favorite movies have been deleted."}
        except Exception as e:
            db.session.rollback()
            return {"error": f"An error occurred while deleting all movies: {str(e)}"}





