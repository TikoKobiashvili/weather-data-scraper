from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app import models
from app.database import Base, engine, SessionLocal

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined list of cities with their latitude and longitude
PREDEFINED_CITIES = [
    {"City": "New York", "Latitude": 40.7128, "Longitude": -74.0060},
    {"City": "Tokyo", "Latitude": 35.6895, "Longitude": 139.6917},
    {"City": "London", "Latitude": 51.5074, "Longitude": -0.1278},
    {"City": "Paris", "Latitude": 48.8566, "Longitude": 2.3522},
    {"City": "Berlin", "Latitude": 52.5200, "Longitude": 13.4050},
    {"City": "Sydney", "Latitude": -33.8688, "Longitude": 151.2093},
    {"City": "Mumbai", "Latitude": 19.0760, "Longitude": 72.8777},
    {"City": "Cape Town", "Latitude": -33.9249, "Longitude": 18.4241},
    {"City": "Moscow", "Latitude": 55.7558, "Longitude": 37.6173},
    {"City": "Rio de Janeiro", "Latitude": -22.9068, "Longitude": -43.1729}
]


def check_if_table_exists(table_name: str):
    """
    Checks if a specific table exists in the database and creates it if it doesn't.
    :param table_name: Name of the table to check
    """
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        logger.info(f"Table '{table_name}' does not exist. Creating table...")
        Base.metadata.create_all(bind=engine, tables=[models.City.__table__])
        logger.info(f"Table '{table_name}' has been created successfully.")
    else:
        logger.info(f"Table '{table_name}' already exists. No action needed.")


def initialize_database():
    """
    Checks if the database is empty. If it is, adds predefined cities.
    """
    db: Session = SessionLocal()
    try:
        # Ensure the "cities" table exists
        check_if_table_exists("cities")

        # Check if the database is empty
        if not db.query(models.City).first():
            logger.info("Database is empty. Adding predefined cities.")

            # Add predefined cities
            for city in PREDEFINED_CITIES:
                db_city = models.City(
                    name=city["City"], latitude=city["Latitude"], longitude=city["Longitude"]
                )
                db.add(db_city)
            db.commit()
            logger.info("Predefined cities have been added to the database.")
        else:
            logger.info("Database already contains cities. No action needed.")
    except SQLAlchemyError as e:
        logger.error(f"Error during database initialization: {str(e)}")
        db.rollback()
    finally:
        db.close()
