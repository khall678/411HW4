import logging
import os
import requests

from boxing.utils.logger import configure_logger
from dotenv import load_dotenv

load_dotenv()

#Get api info
X_RAPIDAPI_KEY = os.getenv('X-RAPIDAPI-KEY')
X_RAPIDAPI_HOST = os.getenv('X-RAPIDAPI-HOST')

logger = logging.getLogger(__name__)
configure_logger(logger)


base_URL = "https://imdb232.p.rapidapi.com/api/search"


def get_movie_info(movie_name):
    """
    Gets movie infromation such as title and release year from imdb232.p.rapidapi.com.

    Returns:
        JSON: Returns the JSON dictonary of info for the movie.

    Raises:
        ValueError: If the response from imdb232.p.rapidapi.com is not a successful status code.
        RuntimeError: If the request to imdb232.p.rapidapi.com fails due to a timeout or other request-related error.

    """
    try:
        logger.info(f"Fetching movie info from {base_URL}")

        url = f"{base_URL}?count=25&type=MOVIE&q={movie_name}"
        headers = {
        "X-RapidAPI-Key": X_RAPIDAPI_KEY,
        "X-RapidAPI-Host": X_RAPIDAPI_HOST
        }

        response = requests.get(url, headers=headers, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        #random_number_str = response.text.strip()
        #
        # try:
        #     random_number = float(random_number_str)
        # except ValueError:
        #     logger.error(f"Invalid response from random.org: {random_number_str}")
        #     raise ValueError(f"Invalid response from random.org: {random_number_str}")
        # I DONT KNOW IF THIS ERROR CHECK IS APPLICABLE

        logger.debug(f"Received a JSON dictonary: {response.json()}")
        logger.info(f"Successfully retrieved movie info")

        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Request to imdb232.p.rapidapi.com timed out.")
        raise RuntimeError("Request to imdb232.p.rapidapi.com timed out.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to imdb232.p.rapidapi.com failed: {e}")
        raise RuntimeError(f"Request to imdb232.p.rapidapi.com failed: {e}")

