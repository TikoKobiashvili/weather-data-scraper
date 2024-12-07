from enum import Enum

from fastapi import FastAPI, Response, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security.api_key import APIKey
from fastapi.responses import FileResponse
from typing import Optional, List
import os

from app.utils.database_init import initialize_database

from app.operations import CitiesOperations, WeatherOperations
from app.process_data import process_weather_data, weather_vizualization
from app.auth import get_api_key


# Define an Enum for value_column options
class DataTypesEnum(str, Enum):
    temperature_c = "Temperature (C)"
    temperature_f = "Temperature (F)"
    humidity = "Humidity (%)"
    wind_speed_ms = "Wind Speed (m/s)"
    wind_speed_mph = "'Wind Speed (mph)"


# Initialize the FastAPI app
app = FastAPI()


@app.on_event("startup")
async def on_startup():
    """
    FastAPI startup event. Initializes the database.
    """
    initialize_database()


# Endpoint to get all cities
@app.get("/cities")
async def get_cities(city_names: Optional[str] = None, api_key: APIKey = Depends(get_api_key)):
    """
    Returns all the cities from the database

    :param api_key: API Key \n
    :param city_names: Name of the city (optional) \n
    :return: cities records from database \n
    """
    cities_operations = CitiesOperations()
    cities = cities_operations.get_cities(city_names=city_names)
    cities_dict = [cities_operations.city_to_dict(city) for city in cities]

    return JSONResponse(content={"cities": cities_dict}, status_code=200)


# Endpoint to add a new city
@app.post("/cities")
async def create_city(city_names: List[str], api_key: APIKey = Depends(get_api_key)):
    """
    Creates city record in database

    :param api_key: API Key \n
    :param city_names: City name, separated by comma (,) \n
    :return: Newly created city information \n
    """
    CitiesOperations().create_city(city_names)

    return JSONResponse(content={"message": f"Cities {city_names} were successfuly created/updated"}, status_code=200)


# Endpoint to fetch weather data and return it as JSON
@app.get("/weather/")
async def get_weather(
        rank_by: Optional[DataTypesEnum] = "Temperature (C)",
        cities_quantity: Optional[int] = None,
        city_names: Optional[str] = None,
        api_key: APIKey = Depends(get_api_key)):
    """
    Processes weather data and returns it as json response

    :param rank_by: To specify by which field processed data should be sorted \n
    :param api_key: API Key\n
    :param city_names:  Name of the cities, seperated by , (comma)  (Optional)\n
    :param cities_quantity: Quantity of the cities to be processed (Optional)\n
    :return: Json response of processed data\n

    WARNING: Only one of 'cities_quantity' or 'city_name' should be provided. Please choose only one
    """
    # Check if both cities_quantity and city_name are provided
    if cities_quantity and city_names:
        raise HTTPException(
            status_code=400,
            detail="Error: Only one of 'cities_quantity' or 'city_name' should be provided. Please choose only one."
        )

    # Fetch weather data for predefined cities
    data = await WeatherOperations().fetch_weather_data_for_cities(cities_quantity, city_names)
    # Process the data using pandas
    processed_data = process_weather_data(weather_data=data, rank_by=rank_by)
    # Return processed data
    return JSONResponse(content={"weather_data": processed_data}, status_code=200)


@app.get("/download-csv/")
async def download_csv_of_processed_weather_data(
        rank_by: Optional[DataTypesEnum] = "Temperature (C)",
        cities_quantity: Optional[int] = None,
        city_names: Optional[str] = None,
        api_key: APIKey = Depends(get_api_key)):
    """
    Processes weather data and downloads CSV for a city based on a name

    :param rank_by: To specify by which field processed data should be sorted \n
    :param api_key: API Key \n
    :param city_names:  Name of the cities, seperated by , (comma)  (Optional) \n
    :param cities_quantity: Quantity of the cities to be processed (optional) \n
    :return: CSV file

    WARNING: Only one of 'cities_quantity' or 'city_names' should be provided. Please choose only one
    """

    # Check if both cities_quantity and city_names are provided
    if cities_quantity and city_names:
        raise HTTPException(
            status_code=400,
            detail="Error: Only one of 'cities_quantity' or 'city_names' should be provided. Please choose only one."
        )

    # Fetch weather data
    data = await WeatherOperations().fetch_weather_data_for_cities(cities_quantity, city_names)

    # Process the data using pandas
    file_path = "weather_data.csv"  # File location
    process_weather_data(weather_data=data, rank_by=rank_by, file_path=file_path)

    if os.path.exists(file_path):  # Check if the file exists
        return FileResponse(file_path, media_type='text/csv', filename="weather_data.csv")
    # If the file does not exist, return an error message
    return Response(content="CSV file not found", status_code=404)


@app.get("/weather-visualization")
async def get_weather_visualization(vizualize_by: DataTypesEnum,
                                    cities_quantity: Optional[int] = None,
                                    city_names: Optional[str] = None,
                                    api_key: APIKey = Depends(get_api_key)):
    """
    Endpoint to fetch and visualize weather data as a bar chart

    :param rank_by: To specify by which field processed data should be sorted \n
    :param vizualize_by: To specify what kind of data needs to be visualized \n
    :param api_key: API Key \n
    :param city_names:  Name of the cities, seperated by , (comma)  (Optional) \n
    :param cities_quantity: Quantity of the cities to be processed (optional) \n
    :return: CSV file

    WARNING: Only one of 'cities_quantity' or 'city_names' should be provided. Please choose only one
    """

    # Check if both cities_quantity and city_names are provided
    if cities_quantity and city_names:
        raise HTTPException(
            status_code=400,
            detail="Error: Only one of 'cities_quantity' or 'city_names' should be provided. Please choose only one."
        )

    # Fetch weather data
    data = await WeatherOperations().fetch_weather_data_for_cities(cities_quantity, city_names)

    data = process_weather_data(weather_data=data)
    try:
        # Generate the image for the specified column
        img_bytes = weather_vizualization(data, vizualize_by)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Return the plot as an image in the response
    return StreamingResponse(img_bytes, media_type="image/png")
