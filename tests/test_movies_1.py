import pytest
from sqlalchemy.exc import IntegrityError
from new_idea.model.movies_model import Movies
from app import create_app, db

@pytest.fixture
def sample_movie_data():
    return {
        "data": {
            "mainSearch": {
                "edges": [
                    {
                        "node": {
                            "entity": {
                                "releaseYear": {"year": 1994},
                                "principalCredits": [
                                    {
                                        "credits": [
                                            {"name": {"nameText": {"text": "Tim Robbins"}}},
                                            {"name": {"nameText": {"text": "Morgan Freeman"}}}
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }
    }

def test_add_favorite_movie_success(app, session, mocker, sample_movie_data):
    mocker.patch("new_idea.model.movies_model.get_movie_info", return_value=sample_movie_data)

    movie = Movies.add_favorite_movie("The Shawshank Redemption")

    assert movie.title == "The Shawshank Redemption"
    assert "Tim Robbins" in movie.actors
    assert movie.year == 1994

def test_add_favorite_movie_duplicate(app, session, mocker, sample_movie_data):
    mocker.patch("new_idea.model.movies_model.get_movie_info", return_value=sample_movie_data)

    # Add the movie for the first time
    Movies.add_favorite_movie("The Shawshank Redemption")

    # Attempt to add the duplicate
    result = Movies.add_favorite_movie("The Shawshank Redemption")
    
    # Assert that the result is None (indicating the movie is a duplicate)
    assert result is None


def test_get_movie_details_success(app, session, mocker, sample_movie_data):
    mocker.patch("new_idea.model.movies_model.get_movie_info", return_value=sample_movie_data)
    Movies.add_favorite_movie("The Shawshank Redemption")

    details = Movies.get_movie_details("The Shawshank Redemption")

    assert details["title"] == "The Shawshank Redemption"
    assert "Tim Robbins" in details["actors"]
    assert details["year"] == 1994

def test_see_all_favorites(app, session, mocker, sample_movie_data):
    mocker.patch("new_idea.model.movies_model.get_movie_info", return_value=sample_movie_data)
    Movies.add_favorite_movie("The Shawshank Redemption")
    Movies.add_favorite_movie("Another Movie")

    favorites = Movies.see_all_favorites()
    assert "The Shawshank Redemption" in favorites
    assert "Another Movie" in favorites

def test_clear_all_favorites(app, session, mocker, sample_movie_data):
    mocker.patch("new_idea.model.movies_model.get_movie_info", return_value=sample_movie_data)
    Movies.add_favorite_movie("The Shawshank Redemption")
    Movies.clear_all_favorites()
    assert Movies.see_all_favorites() == []

def test_delete_favorite_movie(app, session, mocker, sample_movie_data):
    mocker.patch("new_idea.model.movies_model.get_movie_info", return_value=sample_movie_data)
    movie = Movies.add_favorite_movie("The Shawshank Redemption")
    result = Movies.delete_favorite_movie(movie.id)
    assert "deleted_id" in result

def test_add_multiple_favorite_movies(app, session, mocker, sample_movie_data):
    mocker.patch("new_idea.model.movies_model.get_movie_info", return_value=sample_movie_data)

    movie_titles = ["Tag", "Shrek", "The Dark Knight"]
    for title in movie_titles:
        Movies.add_favorite_movie(title)

    # Assert that all movies are added correctly
    favorites = Movies.see_all_favorites()
    assert "Tag" in favorites
    assert "Shrek" in favorites
    assert "The Dark Knight" in favorites

def test_get_multiple_movie_details(app, session, mocker, sample_movie_data):
    mocker.patch("new_idea.model.movies_model.get_movie_info", return_value=sample_movie_data)

    movie_titles = ["Tag", "Shrek", "The Dark Knight"]
    for title in movie_titles:
        Movies.add_favorite_movie(title)

    # Retrieve and verify details for each movie
    for title in movie_titles:
        details = Movies.get_movie_details(title)
        assert details["title"] == title
        assert "Tim Robbins" in details["actors"]
        assert details["year"] == 1994  # Assuming the same sample data is returned for all


