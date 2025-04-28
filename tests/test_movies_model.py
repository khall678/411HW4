import time
import pytest
from new_idea.model.movies_model import Movies
from new_idea import db



@pytest.fixture
def sample_movie1(session):
    """Fixture to provide a sample movie entry."""
    movie = Movies(name="Shrek")
    session.add(movie)
    session.commit()
    return movie


@pytest.fixture
def sample_movie2(session):
    """Fixture to provide another sample movie entry."""
    movie = Movies(name="Finding Nemo")
    session.add(movie)
    session.commit()
    return movie


@pytest.fixture
def sample_movies(sample_movie1, sample_movie2):
    """Fixture to provide a list of sample movies."""
    return [sample_movie1, sample_movie2]


# --- Add Favorite Movie ---
def test_add_favorite_movie(app):
    """Test that a movie can be added to the favorites list."""
    movie = Movies.add_favorite_movie(name="Toy Story", genre="Animation", description="Toys come to life", year="1995")
    assert movie.name == "Toy Story"
    assert movie.genre == "Animation"
    assert movie.description == "Toys come to life"
    assert movie.year == "1995"


# --- Get Favorite Movie ---
def test_get_favorite_movie(app, sample_movie1):
    """Test that a single favorite movie can be retrieved by ID."""
    movie = Movies.get_favorite_movies(sample_movie1.id)
    assert movie is not None
    assert movie.name == sample_movie1.name


# --- View All Favorites ---
def test_view_all_favorites(app, sample_movies):
    """Test that all favorite movies are retrieved."""
    movies = Movies.view_all_favorites()
    assert len(movies) == 2
    assert sample_movies[0].name in [movie.name for movie in movies]
    assert sample_movies[1].name in [movie.name for movie in movies]


# --- See All Favorites (simple list) ---
def test_see_all_favorites(app, sample_movies):
    """Test that a simple list of favorite movies is retrieved."""
    movies = Movies.see_all_favorites()
    assert len(movies) == 2
    assert sample_movies[0].name in [movie.name for movie in movies]
    assert sample_movies[1].name in [movie.name for movie in movies]


# --- Delete Favorite Movie ---
def test_delete_favorite_movie(app, sample_movie1):
    """Test that a favorite movie can be deleted."""
    movie = Movies.delete_favorite_movie(sample_movie1.id)
    assert movie is not None
    assert movie.name == sample_movie1.name
    # Verify movie is deleted from the database
    deleted_movie = Movies.query.get(sample_movie1.id)
    assert deleted_movie is None


# --- Handle Deleting Non-Existing Movie ---
def test_delete_non_existing_movie(app):
    """Test that deleting a non-existing movie returns None."""
    movie = Movies.delete_favorite_movie(99999)  # Assuming this ID doesn't exist
    assert movie is None
