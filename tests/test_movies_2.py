import pytest

from flask_login import login_user
from new_idea.model.user_model import Users
from new_idea import db
from app import create_app

@pytest.fixture
def app():
    """Create and return a test app."""
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB for tests
    with app.app_context():
        db.create_all()  # Create tables before running the tests
    yield app
    with app.app_context():
        db.drop_all()  # Drop tables after tests

@pytest.fixture
def client(app):
    """Provide a test client."""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create and return a test user."""
    user = Users(username="testuser", password="testpassword")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def login_test_user(client, test_user):
    """Log in the test user."""
    with client:
        login_user(test_user)
        yield client  # The test can now use this client to make requests

def test_add_movie(login_test_user):
    """Test adding a movie and checking if it was saved in the database."""
    response = login_test_user.post("/api/add-favorite-movie", json={"title": "The Matrix", "year": 1999, "actors": ["Keanu Reeves", "Laurence Fishburne"]})
    assert response.status_code == 201

def test_get_movies(login_test_user):
    """Test retrieving all movies via the API."""
    response = login_test_user.get("/api/see-all-favorites")
    assert response.status_code == 200
