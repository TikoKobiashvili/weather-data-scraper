from app.database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging
import asyncio

from app.connectors import CitiesConnector, WeatherConnector
from app import models

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseOperations:
    # Dependency to get the DB session
    def get_db(self) -> Session:
        db = SessionLocal()  # Assuming SessionLocal is already defined for database session
        return db


class CitiesOperations:
    def __init__(self):
        # Correctly get the database session
        self.db = DatabaseOperations().get_db()

    @staticmethod
    def city_to_dict(city):
        # Convert the SQLAlchemy model instance to a dictionary
        return {column.name: getattr(city, column.name) for column in city.__table__.columns}

    def create_city(self, city_names):
        """
        Creates or updates a city record in the database.
        If the city already exists, it will update the latitude and longitude.
        If the city doesn't exist, it will create a new record.

        :param city_names: List of the city names
        """
        try:
            # Get lat/long from the external connector
            for name in city_names:
                name = name.capitalize()
                lat, long = CitiesConnector().get_lat_long_from_city(name)

                if lat and long:
                    # Check if the city already exists in the database
                    existing_city = self.db.query(models.City).filter(models.City.name == name).first()

                    if existing_city:
                        # If the city exists, update its latitude and longitude
                        existing_city.latitude = lat
                        existing_city.longitude = long
                        self.db.commit()  # Commit the changes to the database
                        self.db.refresh(existing_city)  # Refresh the city record to get the updated info
                    else:
                        # If the city does not exist, create a new city record
                        db_city = models.City(name=name, latitude=lat, longitude=long)
                        self.db.add(db_city)
                        self.db.commit()  # Commit the new city to the database
                        self.db.refresh(db_city)  # Refresh the city record to get the latest info
        except Exception as e:
            self.db.rollback()  # Rollback the transaction if something goes wrong
            raise e
        finally:
            self.db.close()  # Close the session when done

    def get_cities(self, quantity=None, city_names=None):
        """
        Returns existing cities records from the database.
        :return: List of cities or an HTTPException if an error occurs.
        """
        try:
            # If quantity was provided
            if quantity:
                available_cities_count = self.db.query(models.City).count()
                # Ensure that the quantity does not exceed the available number of cities
                cities = self.db.query(models.City).limit(min(quantity, available_cities_count)).all()
            # If list of city names was provided
            elif city_names:
                cities_list = city_names.split(',')
                cities_list = [city.strip().capitalize() for city in cities_list]
                cities = self.db.query(models.City).filter(models.City.name.in_(cities_list)).all()
            # Returns everything from db
            else:
                cities = self.db.query(models.City).all()
            if not cities:
                raise HTTPException(status_code=404, detail="No cities found in the database.")
            return cities

        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching cities: {str(e)}")
            raise HTTPException(status_code=500, detail="An error occurred while fetching cities from the database.")


class WeatherOperations:
    # Open-Meteo API base URL
    API_URL = "https://api.open-meteo.com/v1/forecast"

    async def fetch_weather_data_for_cities(self, quantity=None, city_names=None):
        """
        Fetch weather data for all cities.
        :return: Weather data for all cities or an HTTPException if an error occurs.
        """
        try:
            # Fetch all cities
            cities = CitiesOperations().get_cities(quantity, city_names)
            if not cities:
                raise HTTPException(status_code=404, detail="No cities found to fetch weather data.")

            # Fetch weather data for all cities
            try:
                # Create an async task for each city
                tasks = [WeatherConnector().get_weather_data(city) for city in cities]

                # Run all tasks concurrently and gather results
                weather_data = await asyncio.gather(*tasks)
                # Filter out any cities that failed to get weather data
                return [data for data in weather_data if data is not None]

            except Exception as e:
                logger.error(f"Error fetching weather data for cities: {str(e)}")
                raise HTTPException(status_code=500, detail="An error occurred while fetching weather data for cities.")

        except HTTPException:
            # Propagate already-raised HTTP exceptions (e.g., from `get_cities`)
            raise
        except SQLAlchemyError as e:
            # Handle database-related errors
            logger.error(f"Database error while fetching cities: {str(e)}")
            raise HTTPException(status_code=500, detail="An error occurred while retrieving cities from the database.")
