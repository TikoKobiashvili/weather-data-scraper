import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from app.operations import CitiesOperations


@pytest.fixture
def mocked_db_session():
    """Fixture to provide a mocked database session."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mocked_connector():
    """Fixture to mock the CitiesConnector."""
    with patch("connectors.CitiesConnector") as MockConnector:
        connector = MockConnector.return_value
        yield connector


@pytest.fixture
def cities_operations(mocked_db_session):
    """Fixture to provide an instance of CitiesOperations with a mocked DB."""
    ops = CitiesOperations()
    ops.db = mocked_db_session
    return ops


def test_create_city_add_new_city(mocked_db_session, mocked_connector, cities_operations):
    """Test that a new city is created when it doesn't already exist."""
    # Mock the external connector
    mocked_connector.get_lat_long_from_city.return_value = (34.0522, -118.2437)

    # Mock the database query to return no existing city
    mocked_db_session.query.return_value.filter.return_value.first.return_value = None

    # Mock adding a city to the database
    mocked_db_session.add = MagicMock()

    # Call the create_city method
    cities_operations.create_city(["Los Angeles"])

    # Assert the city was added and committed
    mocked_db_session.add.assert_called_once()
    mocked_db_session.commit.assert_called_once()


# Test get_cities method
def test_get_cities_by_quantity(mocked_db_session, cities_operations):
    """Test fetching a limited number of cities."""
    # Mock the database query
    mocked_db_session.query.return_value.count.return_value = 10
    mocked_db_session.query.return_value.limit.return_value.all.return_value = ["City1", "City2"]

    # Call the get_cities method
    cities = cities_operations.get_cities(quantity=2)

    # Assert the correct number of cities is returned
    assert cities == ["City1", "City2"]


def test_get_cities_by_names(mocked_db_session, cities_operations):
    """Test fetching cities by a list of names."""
    # Mock the database query
    mocked_db_session.query.return_value.filter.return_value.all.return_value = ["City1", "City2"]

    # Call the get_cities method
    cities = cities_operations.get_cities(city_names="City1,City2")

    # Assert the correct cities are returned
    assert cities == ["City1", "City2"]


def test_get_all_cities(mocked_db_session, cities_operations):
    """Test fetching all cities when no filters are provided."""
    # Mock the database query
    mocked_db_session.query.return_value.all.return_value = ["City1", "City2", "City3"]

    # Call the get_cities method
    cities = cities_operations.get_cities()

    # Assert all cities are returned
    assert cities == ["City1", "City2", "City3"]


def test_get_cities_no_results(mocked_db_session, cities_operations):
    """Test fetching cities when no results are found."""
    # Mock the database query to return no cities
    mocked_db_session.query.return_value.all.return_value = []

    # Call the get_cities method and expect an exception
    with pytest.raises(HTTPException) as exc_info:
        cities_operations.get_cities()

    # Assert the exception is raised with the correct status and detail
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "No cities found in the database."
