import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DataManager:

    def __init__(self):
        self.sheety_token = os.environ["SHEETY_TOKEN"]
        self.sheety_endpoint = os.environ["SHEETY_PRICES_ENDPOINT"]
        self.sheety_header = {
            "Authorization": self.sheety_token
        }
        self.destination_data = {}

    def get_destination_data(self):
        # Use the Sheety API to GET all the data in that Google sheet.

        response = requests.get(url=self.sheety_endpoint, headers=self.sheety_header)
        data = response.json()
        self.destination_data = data["prices"]

        return self.destination_data

    # Update the Google Sheet with the IATA codes if they do not exist and only the city name was input.
    def update_destination_codes(self):
        for city in self.destination_data:
            new_data = {
                "price": {
                    "iataCode": city["iataCode"]
                }
            }

            response = requests.put(url=f"{self.sheety_endpoint}/{city['id']}", json=new_data, headers=self.sheety_header)