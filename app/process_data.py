import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import io


# Function to process weather data using pandas
def process_weather_data(weather_data, rank_by='Temperature (C)', file_path=None, ):
    # Create a pandas DataFrame from the raw weather data
    df = pd.DataFrame(weather_data)

    # Convert temperature from Celsius to Fahrenheit
    df["Temperature (F)"] = df["Temperature (C)"] * 9 / 5 + 32

    # Convert wind speed from meters per second to miles per hour
    df["Wind Speed (mph)"] = df["Wind Speed (m/s)"] * 2.23694

    # Sort the data based on the rank_by column (default: 'Temperature (C)')
    df_sorted = df.sort_values(by=rank_by, ascending=False)

    if file_path:
        # Export the processed DataFrame to a CSV file
        df_sorted.to_csv(file_path, index=False)

    # Return the processed and sorted data as a dictionary for use in the API
    return df_sorted.to_dict(orient="records")


def weather_vizualization(weather_data, vizualize_by):
    # Convert the weather data to a pandas DataFrame
    df = pd.DataFrame(weather_data)

    # Check if the vizualize_by exists in the DataFrame
    if vizualize_by not in df.columns:
        raise ValueError(f"'{vizualize_by}' is not a valid column in the weather data")

    # Create a new figure to ensure a clean slate for the plot
    fig, ax = plt.subplots(figsize=(10, 6))  # Create figure and axes objects
    sns.barplot(data=df, x='City', y=vizualize_by, palette='coolwarm', ax=ax)  # Pass the Axes object

    # Set title and labels dynamically
    ax.set_title(f'{vizualize_by} by City')
    ax.set_xlabel('City')
    ax.set_ylabel(f'{vizualize_by}')

    # Save the plot to a BytesIO object
    img_bytes = io.BytesIO()
    fig.savefig(img_bytes, format='png')  # Save the figure
    img_bytes.seek(0)

    # Close the figure to free memory
    plt.close(fig)

    return img_bytes
