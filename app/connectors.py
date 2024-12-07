import requests
import logging
import asyncio
import httpx

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CitiesConnector:
    def __init__(self):
        self.cities_api = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }

    def get_lat_long_from_city(self, city_name):
        # Parameters to be passed to the API
        params = {
            "q": city_name,
            "format": "json"
        }
        try:
            # Send GET request to OpenCage Geocoding API
            response = requests.get(self.cities_api, headers=self.headers, params=params)

            # Check if the response was successful (HTTP status code 200)
            if response.status_code == 200:
                data = response.json()

                # Check if any results were returned
                if data:
                    # Extract latitude and longitude
                    lat = data[0]['lat']
                    lon = data[0]['lon']
                    logger.info(f"The latitude and longitude of {city_name} are {lat}, {lon}")
                    return lat, lon
                else:
                    logger.warning(f"No results found for {city_name}.")
                    return None, None  # No results found
            else:
                logger.error(
                    f"Error: Received status code {response.status_code} from API: {self.cities_api},params: {params}")
                return None, None
        except requests.exceptions.RequestException as e:
            # Catch any request errors (network issues, invalid URL, etc.)
            logger.error(f"Request error: {e}")
            return None, None


class WeatherConnector:

    def __init__(self):
        self.weather_api = "https://api.open-meteo.com/v1/forecast"

    async def get_weather_data(self, city):

        # Extract latitude, longitude, and city name from the model instance
        city_name = city.name
        latitude = city.latitude
        longitude = city.longitude

        # Parameters to be passed to the API
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True  # Request current weather data
        }

        try:
            # Send GET request to the weather API
            async with httpx.AsyncClient() as client:
                response = await client.get(self.weather_api, params=params)

            # Check if the response was successful (HTTP status code 200)
            if response.status_code == 200:
                data = response.json().get("current_weather", {})

                # Check if any results were returned
                if data:
                    # Parse the response JSON and extract relevant data
                    return {
                        "City": city_name,
                        "Temperature (C)": data.get("temperature"),  # Temperature in Celsius
                        "Wind Speed (m/s)": data.get("windspeed"),  # Wind speed in meters per second
                        "Humidity (%)": data.get("humidity"),  # Humidity percentage
                    }
                else:
                    logger.warning(f"No weather data found for city: {city_name}.")
            else:
                logger.error(
                    f"Error: Received status code {response.status_code} from API: {self.weather_api}, params: {params}")
        except requests.exceptions.RequestException as e:
            # Catch any request errors (network issues, invalid URL, etc.)
            logger.error(f"Request error: {e}")

