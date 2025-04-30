import pytest
from app import create_app, db  # Adjust imports to match your structure
from new_idea.model.movies_model import Movies
from new_idea.model.user_model import Users

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')  # Use the 'testing' config for test setup
    return app

@pytest.fixture(scope='module')
def session(app):
    """Create a new database session for testing."""
    with app.app_context():
        db.create_all()  # Create all tables for testing
        yield db.session  # Provide the session for the test
        db.drop_all()  # Clean up after tests
