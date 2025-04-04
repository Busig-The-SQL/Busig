import pytest

from bus_model.app import create_app
from bus_model.config import TestConfig

@pytest.fixture()
def app():
    """Create a Flask application instance for testing."""
    app = create_app(TestConfig)
    with app.app_context():
        yield app


@pytest.fixture()
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()