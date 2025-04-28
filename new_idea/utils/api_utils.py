import logging
import os
import requests

from movies.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


RANDOM_ORG_URL = os.getenv("RANDOM_ORG_URL",
                           "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new")

def get_movie_info_from_api(title: str):
   
    api_url = f"http://www.omdbapi.com/?t={title}&apikey=6725ea5f75msh12509b1a22fff49p1e16cejsn1bb65eb56a85"
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        movie_data = response.json()
        return {
            "title": movie_data["Title"],
            "director": movie_data["Director"],
            "genre": movie_data["Genre"],
            "year": movie_data["Year"]
        }
    else:
        raise ValueError(f"API request failed for {title}")

