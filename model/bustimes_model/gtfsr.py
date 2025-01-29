"""
Provides a class to query GTFSR API
"""

import os
import urllib.request
import json
from dotenv import load_dotenv


class GTFSR:
    """
    Queries the GTFSR API
    """

    def __init__(self):
        self.configure()
        self.base_url = "https://api.nationaltransport.ie/gtfsr/v2/"
        self.json_format = "?format=json"
        self.api_key = os.environ.get("api_key")

    def configure(self):
        load_dotenv()

    def fetch_gtfsr(self):
        return self.fetch_endpoint("gtfsr")

    def fetch_vehicles(self):
        return self.fetch_endpoint("Vehicles")

    def fetch_tripUpdates(self):
        return self.fetch_endpoint("TripUpdates")

    def fetch_endpoint(self, endpoint):
        try:
            url = self.base_url+endpoint+self.json_format
            hdr = {            # Request headers
                'Cache-Control': 'no-cache',
                'x-api-key': self.api_key,
            }

            req = urllib.request.Request(url, headers=hdr)

            req.get_method = lambda: 'GET'
            response = urllib.request.urlopen(req)
            response_data = response.read().decode('utf-8')
            json_data = json.loads(response_data)
            return json_data

        except Exception as e:
            print(f"Error occured when connecting to and endpoint{e}")

    def print_json(self, json_data):
        """prints the provided json data"""
        print(json.dumps(json_data, indent=4))

    def create_json_file(self, filename, json_data):
        """creates a json file in the directory from the given json data"""
        try:
            with open(filename, "w") as json_file:
                json.dump(json_data, json_file)
        except Exception as e:
            print(f"Error occured when creating a json file: {e}")


if __name__ == "__main__":
    gtfsr = GTFSR()
    json_vehicle_data = gtfsr.fetch_vehicles()
    # gtfsr.print_json(json_data)
    gtfsr.create_json_file("vehicles.json", json_vehicle_data)
    json_trip_data = gtfsr.fetch_tripUpdates()
    gtfsr.create_json_file("tripUpdates.json", json_trip_data)
