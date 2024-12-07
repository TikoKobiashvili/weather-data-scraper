# Weather Data Scraping API

This project is a FastAPI-based application for scraping weather data from the Open-Meteo API. The application fetches current weather data (temperature, wind speed, and humidity) for a predefined list of cities, processes the data using pandas, and exports it to a CSV file. The processed data can also be accessed through API endpoints.

## Features
- **Fetch Weather Data**: Scrapes weather data (temperature, wind speed, and humidity) for 10 predefined cities using the Open-Meteo API.
- **Database**:
  - Stores predefined cities in an SQLite database.
  - Endpoints to interact with the database (GET and POST).
- **Data Processing**:
  - Converts temperatures from Celsius to Fahrenheit.
  - Converts wind speed from meters per second to miles per hour.
- **Export to CSV**: Saves processed weather data into `weather_data.csv`.
- **API Endpoints**:
  - Fetch weather data.
  - Download the CSV file.
  - Visualize processed weather data.
- **Dockerized**: Easily deployable using Docker.

## Requirements
- Python 3.9+
- Docker
- Other requirements can be seen in requirements.txt

## Technologies Used
- **FastAPI**: Web framework for building the API.
- **SQLAlchemy**: ORM for interacting with the SQLite database.
- **SQLite**: Lightweight database for storing cities.
- **Pandas**: Data manipulation and processing.
- **Requests**: To make HTTP calls to the Open-Meteo API.
- **Uvicorn**: ASGI server for serving the FastAPI application.
- **Docker**: For containerization.

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/TikoKobiashvili/weather-data-scraper.git
cd weather-data-scraper
```
### 2. Create virtual environment
```bash
python -m venv <virtual-environment-name>
```
#### Activate virtual environment
```bash
source <virtual-environment-name>/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Copy the Sample Environment File
For local development, setting up environment variables is necessary. Copy the provided `.env.sample` file to
create your own `.env` file. Update the values according to your configuration.
This file contains essential settings for environment-specific variables.

Copy the contents of `.env.sample`:

```bash
cp .env.sample .env
```

### 5. Run the Application Using Docker

Build and run the app using Docker:
```bash
docker-compose up --build
```
The app will be available at http://localhost:8000.

### 6. Run tests

```bash
docker-compose run --no-deps app bash -c "coverage run -m pytest app; coverage report -m; coverage html; coverage xml"
```

### 7. API Endpoints
#### API Key - secret

- **Access Swagger UI**: `http://localhost:8000/docs#/`
  - Displays available endpoints.
- **Fetch cities**: `GET /cities`
  - Retrieves all cities from the database.
  - Retrieves list of cities based on the names specified in params. Names should be separated by comma (,)
- **Add City**: `POST /cities`
  - Adds a new city/cities to the database. You need to provide a name(s).
- **Fetch Weather Data**: `GET /weather`
  - Returns processed weather data for the cities in JSON format.
  - Returns processed weather data for list of cities based on the names specified in params. (names should be separated by comma (,))
  - Returns processed weather data for quantity of cities, specified in params.
- **Download CSV**: `GET /download-csv`
  - Provides the processed weather data for all the cities, as a downloadable CSV file.
  - Provides the processed weather data for list cities based on the names specified in params, as a downloadable CSV file.(names should be separated by comma (,))
  - Provides the processed weather data for quantity of cities, specified in params, as a downloadable CSV file.
- **Visualize process data**: `GET /weather-visualization`
  - Provides the processed weather data visualization for all the cities, as an image.
  - Provides the processed weather data visualization for list cities based on the names specified in params, as an image.(names should be separated by comma (,))
  - Provides the processed weather data visualization for quantity of cities, specified in params, as an image.


## Predefined Cities
The application fetches weather data for the following cities, if database is empty:
- New York
- Tokyo
- London
- Paris
- Berlin
- Sydney
- Mumbai
- Cape Town
- Moscow
- Rio de Janeiro


## Files

- **docker-compose.yml**: Docker Compose configuration file.
- **Dockerfile**: Docker configuration file for building the microservice image.
- **requirements.txt**: List of Python dependencies.
- **.env.sample**: sample for environment variables
