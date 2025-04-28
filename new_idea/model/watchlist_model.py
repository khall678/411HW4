import logging
import os
import time
from typing import List

from watchlist.models.movie_model import Movies
from watchlist.utils.api_utils import get_random
from watchlist.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

class WatchlistModel:
    """
    A class to manage a watchlist of movies.
    """

    def __init__(self):
        """Initializes the WatchlistModel with an empty watchlist.

        The watchlist is a list of Movies.
        The TTL (Time To Live) for movie caching is set to a default value from the environment variable "TTL",
        which defaults to 60 seconds if not set.
        """
        self.watchlist: List[int] = []
        self._movie_cache: dict[int, Movies] = {}
        self._ttl: dict[int, float] = {}
        self.ttl_seconds = int(os.getenv("TTL", 60))

    ##################################################
    # Movie Management Functions
    ##################################################

    def _get_movie_from_cache_or_db(self, movie_id: int) -> Movies:
        now = time.time()

        if movie_id in self._movie_cache and self._ttl.get(movie_id, 0) > now:
            logger.debug(f"Movie ID {movie_id} retrieved from cache")
            return self._movie_cache[movie_id]

        try:
            movie = Movies.get_movie_by_id(movie_id)
            logger.info(f"Movie ID {movie_id} loaded from DB")
        except ValueError as e:
            logger.error(f"Movie ID {movie_id} not found in DB: {e}")
            raise ValueError(f"Movie ID {movie_id} not found in database") from e

        self._movie_cache[movie_id] = movie
        self._ttl[movie_id] = now + self.ttl_seconds
        return movie

    def add_movie_to_watchlist(self, movie_id: int) -> None:
        logger.info(f"Received request to add movie with ID {movie_id} to the watchlist")

        movie_id = self.validate_movie_id(movie_id, check_in_watchlist=False)

        if movie_id in self.watchlist:
            logger.error(f"Movie with ID {movie_id} already exists in the watchlist")
            raise ValueError(f"Movie with ID {movie_id} already exists in the watchlist")

        try:
            movie = self._get_movie_from_cache_or_db(movie_id)
        except ValueError as e:
            logger.error(f"Failed to add movie: {e}")
            raise

        self.watchlist.append(movie.id)
        logger.info(f"Successfully added to watchlist: {movie.director} - {movie.title} ({movie.year})")

    def remove_movie_by_movie_id(self, movie_id: int) -> None:
        logger.info(f"Received request to remove movie with ID {movie_id}")

        self.check_if_empty()
        movie_id = self.validate_movie_id(movie_id)

        if movie_id not in self.watchlist:
            logger.warning(f"Movie with ID {movie_id} not found in the watchlist")
            raise ValueError(f"Movie with ID {movie_id} not found in the watchlist")

        self.watchlist.remove(movie_id)
        logger.info(f"Successfully removed movie with ID {movie_id} from the watchlist")

    def clear_watchlist(self) -> None:
        logger.info("Received request to clear the watchlist")

        try:
            if self.check_if_empty():
                pass
        except ValueError:
            logger.warning("Clearing an empty watchlist")

        self.watchlist.clear()
        logger.info("Successfully cleared the watchlist")

    ##################################################
    # Watchlist Retrieval Functions
    ##################################################

    def get_all_movies(self) -> List[Movies]:
        self.check_if_empty()
        logger.info("Retrieving all movies in the watchlist")
        return [self._get_movie_from_cache_or_db(movie_id) for movie_id in self.watchlist]

    def get_movie_by_movie_id(self, movie_id: int) -> Movies:
        self.check_if_empty()
        movie_id = self.validate_movie_id(movie_id)
        logger.info(f"Retrieving movie with ID {movie_id} from the watchlist")
        movie = self._get_movie_from_cache_or_db(movie_id)
        logger.info(f"Successfully retrieved movie: {movie.director} - {movie.title} ({movie.year})")
        return movie

    def get_watchlist_length(self) -> int:
        length = len(self.watchlist)
        logger.info(f"Retrieving watchlist length: {length} movies")
        return length

    ##################################################
    # Utility Functions
    ##################################################

    def validate_movie_id(self, movie_id: int, check_in_watchlist: bool = True) -> int:
        try:
            movie_id = int(movie_id)
            if movie_id < 0:
                raise ValueError
        except ValueError:
            logger.error(f"Invalid movie id: {movie_id}")
            raise ValueError(f"Invalid movie id: {movie_id}")

        if check_in_watchlist and movie_id not in self.watchlist:
            logger.error(f"Movie with id {movie_id} not found in watchlist")
            raise ValueError(f"Movie with id {movie_id} not found in watchlist")

        try:
            self._get_movie_from_cache_or_db(movie_id)
        except Exception as e:
            logger.error(f"Movie with id {movie_id} not found in database: {e}")
            raise ValueError(f"Movie with id {movie_id} not found in database")

        return movie_id

    def check_if_empty(self) -> None:
        if not self.watchlist:
            logger.error("Watchlist is empty")
            raise ValueError("Watchlist is empty")
