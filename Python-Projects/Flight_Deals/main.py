"""Flight Deals International
By George Sandoval

Program that is designed to find flight deals based on a list of desired destination within a certain timeframe
and sends a text if a deal is found

1: Check google sheet data and make sure the destination cities in the sheet have IATA codes. If not, then populate them
2: Use the IATA codes to search for prices from the origin city to the destination cities
3 If the round trip prices found between tomorrow and 6 months from now are cheaper than what is currently stored
in the Google Sheet, then send an SMS or Whatsapp message to the user so that they can book the flight.
"""

import time
from datetime import datetime, timedelta
import notification_manager
from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import find_cheapest_flight

data_manager = DataManager()
sheet_data = data_manager.get_destination_data()
flight_search = FlightSearch()

# Set the origin airport IATA Code
ORIGIN_CITY_IATA = "DEN"

#Check the IATA code exists in the sheet. If not, then update the sheet with the IATA code using the city name
for row in sheet_data:
    if row["iataCode"] == "":
        row["iataCode"] = flight_search.get_destination_code(row["city"])
        # slowing down requests to avoid rate limit
        time.sleep(2)

data_manager.destination_data = sheet_data
data_manager.update_destination_codes()

#Set the time frame here. Default is between tomorrow and 6 months from now.
tomorrow = datetime.now() + timedelta(days=1)
six_month_from_today = datetime.now() + timedelta(days=(6 * 30))

#Get round trip flight info for each destination in the sheet and record the cheapest flight
for destination in sheet_data:
    print(f"Getting flights for {destination['city']}...")
    flights = flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination["iataCode"],
        from_time=tomorrow,
        to_time=six_month_from_today
    )
    cheapest_flight = find_cheapest_flight(flights)
    print(f"{destination['city']}: ${cheapest_flight.price}")
    # Slowing down requests to avoid rate limit
    time.sleep(2)

    #If the cheapest flight found is cheaper than the price recorded in the sheet,
    # then send a text to the user with the info
    if cheapest_flight.price != "N/A" and cheapest_flight.price < destination["lowestPrice"]:
        print(f"Lower price flight found to {destination['city']}!")
        #Code for sending an SMS instead of Whatsapp message
        # notification_manager.send_sms(
        #     message_body=f"Low price alert! Only £{cheapest_flight.price} to fly "
        #                  f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, "
        #                  f"on {cheapest_flight.out_date} until {cheapest_flight.return_date}."
        # )

        # Whatsapp instead.
        notification_manager.NotificationManager.send_whatsapp(
            message_body=f"Low price alert! Only ${cheapest_flight.price} to fly "
                         f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, "
                         f"on {cheapest_flight.depart_date} until {cheapest_flight.return_date}."
        )