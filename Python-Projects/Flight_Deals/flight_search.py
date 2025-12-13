import os
import requests
from datetime import datetime
from dotenv import load_dotenv

#Load environment variables
load_dotenv()

class FlightSearch:

    def __init__(self):
        self._api_key = os.environ["AMADEUS_API_KEY"]
        self._api_secret = os.environ["AMADEUS_SECRET"]
        self._iata_endpoint = os.environ["AMADEUS_IATA_ENDPOINT"]
        self._token_endpoint = os.environ["AMADEUS_TOKEN_ENDPOINT"]
        self._flight_endpoint = os.environ["AMADEUS_FLIGHT_ENDPOINT"]
        self._token = self._get_new_token()

    def _get_new_token(self):
        #Retrieve the token from the API that is required in order to make calls to the Amadeus API. Lasts 30 minutes.
        header = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        body = {
            'grant_type': 'client_credentials',
            'client_id': self._api_key,
            'client_secret': self._api_secret
        }

        response = requests.post(url=self._token_endpoint, headers=header, data=body)
        data = response.json()
        # New bearer token. Typically expires in 1799 seconds (30min)
        access_token = data["access_token"]

        return access_token

    def get_destination_code(self, city_name):
        """
        Retrieves the IATA code for a specified city using the Amadeus Location API.
        Parameters:
        city_name (str): The name of the city for which to find the IATA code.
        Returns:
        str: The IATA code of the first matching city if found; "N/A" if no match is found due to an IndexError,
        or "Not Found" if no match is found due to a KeyError.

        The function sends a GET request to the IATA_ENDPOINT with a query that specifies the city
        name and other parameters to refine the search. It then attempts to extract the IATA code
        from the JSON response.
        - If the city is not found in the response data, it logs a message
        indicating that no airport code was found for the city and
        returns "N/A".
        - If the expected key is not found in the response, it logs a message
        indicating that no airport code was found for the city
        and returns "Not Found".
        """
        headers = {"Authorization": f"Bearer {self._token}"}
        query = {
            "keyword": city_name,
            "max": "2",
            "include": "AIRPORTS",
        }
        response = requests.get(
            url=self._iata_endpoint,
            headers=headers,
            params=query
        )

        #Status codes and error handling here for missing airport codes
        print(f"Status code {response.status_code}. Airport IATA: {response.text}")
        try:
            code = response.json()["data"][0]['iataCode']
        except IndexError:
            print(f"IndexError: No airport code found for {city_name}.")
            return "N/A"
        except KeyError:
            print(f"KeyError: No airport code found for {city_name}.")
            return "Not Found"

        return code

    def check_flights(self, origin_city_code, destination_city_code, from_time, to_time):
        """
        Searches for flight options between two cities on specified departure and return dates
        using the Amadeus API.
        Parameters:
            origin_city_code (str): The IATA code of the departure city.
            destination_city_code (str): The IATA code of the destination city.
            from_time (datetime): The departure date.
            to_time (datetime): The return date.
        Returns:
            dict or None: A dictionary containing flight offer data if the query is successful; None
            if there is an error.
        The function constructs a query with the flight search parameters and sends a GET request to
        the API. We handle the response by checking the status code and parsing the JSON data if the
        request is successful. If the response status code is not 200, it logs an error message and
        provides a link to the API documentation for status code details and troubleshooting.
        """

        headers = {"Authorization": f"Bearer {self._token}"}
        query = {
            "originLocationCode": origin_city_code,
            "destinationLocationCode": destination_city_code,
            "departureDate": from_time.strftime("%Y-%m-%d"),
            "returnDate": to_time.strftime("%Y-%m-%d"),
            "adults": 1,
            "nonStop": "true",
            "currencyCode": "USD",
            "max": "10",
        }

        response = requests.get(
            url=self._flight_endpoint,
            headers=headers,
            params=query,
        )

        if response.status_code != 200:
            print(f"check_flights() response code: {response.status_code}")
            print("There was a problem with the flight search.\n"
                  "For details on status codes, check the API documentation:\n"
                  "https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search/api"
                  "-reference")
            print("Response body:", response.text)
            return None

        return response.json()