import requests
import os
import csv
import bus_model
import datetime
import time

from dotenv import load_dotenv
from GTFS_Static.db_connection import create_connection, close_connection


load_dotenv()

def manage_read_only_connection(func):
    def wrapper(*args, **kwargs):
        conn = create_connection()
        cursor = conn.cursor()
        try:
            func(cursor, *args, **kwargs)
            return cursor.fetchall()
        finally:
            close_connection(conn)
    return wrapper

class GTFSR:
    """A class to make requests to the GTFSR API. All methods can be used without initialising the class."""
    base_url = "https://api.nationaltransport.ie/gtfsr/v2/"
    format_json = "?format=json"
    api_key = os.getenv("api_key", None)

    @classmethod
    def fetch_vehicles(self) -> dict:
        """
        Fetches the vehicles endpoint from the GTFSR API.

        Returns:
            dict: The response from the GTFSR API
        """
        return self.fetch_endpoint("Vehicles")

    @classmethod
    def fetch_trip_updates(self) -> dict:
        """
        Fetches the trip_updates endpoint from the GTFSR API.

        Returns:
            dict: The response from the GTFSR API
        """
        return self.fetch_endpoint("TripUpdates")

    @classmethod
    def fetch_gtfsr(self) -> dict:
        """
        Fetches the gtfsr endpoint from the GTFSR API.

        Returns:
            dict: The response from the GTFSR API
        """
        return self.fetch_endpoint("gtfsr")

    @classmethod
    def fetch_endpoint(self, endpoint: str) -> dict:
        """
        Makes a request to the GTFSR API at the specified endpoint.

        Returns:
            dict: A JSON formatted response from the GTFSR API
        """
        url = self.base_url + endpoint + self.format_json
        headers = {
            'Cache-Control': 'no-cache',
            'x-api-key': self.api_key
        }

        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            print(e)
            return None
        return response.json()


class StaticGTFSR:
    """A class to parse GTFSR data from the PostgreSQL db."""
    static_folder = "back-end/static_gtfsr/"
    agency  = static_folder + "agency.txt"
    stops   = static_folder + "stops.txt"
    routes  = static_folder + "routes.txt"
    trips   = static_folder + "trips.txt"
    stop_times = static_folder + "stop_times.txt"   # "cork_stop_times.txt"
    calendar = static_folder + "calendar.txt"
    calendar_dates = static_folder + "calendar_dates.txt"
    shapes = static_folder + "shapes.txt"
    feed_info = static_folder + "feed_info.txt"
    date_format = "%Y%m%d"
    time_format = "%H:%M:%S"
    cork_trip_ids = static_folder + "cork_trip_ids.txt"

    @classmethod
    def read_routes(self, path=routes):
        with open(path, 'r', encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                bus_model.Route(row['route_id'], row['agency_id'],
                                row['route_short_name'], row['route_long_name'], row['route_type'])

    @classmethod
    def read_stops(self, path=stops):
        with open(path, 'r', encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                bus_model.Stop(row['stop_id'], row['stop_code'] or None,
                               row['stop_name'], row['stop_lat'], row['stop_lon'])

    @classmethod
    def read_agencies(self, path=agency):
        with open(path, 'r', encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                bus_model.Agency(row['agency_id'], row['agency_name'])

    @classmethod
    def read_calendar(self, path=calendar):
        with open(path, 'r', encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                start_date = datetime.datetime.strptime(
                    row['start_date'], self.date_format)
                end_date = datetime.datetime.strptime(
                    row['end_date'], self.date_format)
                bus_model.Service(row['service_id'], row['monday'], row['tuesday'], row['wednesday'],
                                  row['thursday'], row['friday'], row['saturday'], row['sunday'], start_date, end_date)

    @classmethod
    def read_calendar_dates(self, path=calendar_dates):
        with open(path, 'r', encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                date = datetime.datetime.strptime(
                    row['date'], self.date_format)
                service = bus_model.Service._all[row['service_id']]
                service.add_exception(date, int(row['exception_type']))

    @classmethod
    def read_shapes(self, path=shapes):
        with open(path, 'r', encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                shape_id = row['shape_id']
                if shape_id not in bus_model.Shape._all:
                    shape = bus_model.Shape(shape_id)
                else:
                    shape = bus_model.Shape._all[shape_id]
                shape.add_point(row['shape_pt_lat'], row['shape_pt_lon'])

    @classmethod
    def read_trips(self, path=trips):
        with open(path, 'r', encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                bus_model.Trip(row['trip_id'], row['route_id'], row['service_id'], row['shape_id'],
                               row['trip_headsign'], row['trip_short_name'], row['direction_id'], row['block_id'])

    @classmethod
    def read_stop_times(self, path=stop_times):
        # with open(self.cork_trip_ids, 'r', encoding="utf-8") as csv_file:
        #     cork_trip_ids = set(csv_file.read().splitlines())

        with open(path, 'r', encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                # if row['trip_id'] not in cork_trip_ids:    # Filter to cork times only to reduce size from 250mb
                #     continue

                # datetime only allows times between 0-23, so adjust the 24-29h times
                if (t := int(row['arrival_time'][:2])) > 23:
                    row['arrival_time'] = "0" + str(t-24) + row['arrival_time'][2:]
                if (t := int(row['departure_time'][:2])) > 23:
                    row['departure_time'] = "0" + str(t-24) + row['departure_time'][2:]
                arrival_time = datetime.datetime.strptime(
                    row['arrival_time'], self.time_format).time()
                departure_time = datetime.datetime.strptime(
                    row['departure_time'], self.time_format).time()
                
                bus_model.BusStopVisit(row['trip_id'], row['stop_id'], arrival_time, departure_time, row['stop_sequence'],
                                       row['stop_headsign'], row['pickup_type'], row['drop_off_type'], row['timepoint'])

    @classmethod
    def load_all_files(self):
        t = time.time()
        self.read_agencies()
        print(f"Agencies loaded in {(t1:=time.time()) - t}s")
        self.read_calendar()
        print(f"Calendar loaded in {(t:=time.time()) - t1}s")
        self.read_stops()
        print(f"Stops loaded in {(t1:=time.time()) - t}s")
        self.read_shapes()
        print(f"Shapes loaded in {(t:=time.time()) - t1}s")
        self.read_routes()
        print(f"Routes loaded in {(t1:=time.time()) - t}s")
        self.read_calendar_dates()
        print(f"Calendar dates loaded in {(t:=time.time()) - t1}s")
        self.read_trips()
        print(f"Trips loaded in {(t1:=time.time()) - t}s")
        self.read_stop_times()
        print(f"Stop times loaded in {(t:=time.time()) - t1}s")


if __name__ == "__main__":
    # quick debugging
    import time
    start = time.time()
    StaticGTFSR.load_all_files()
    #print("num visits", len(bus_model.Trip._all))
    print(f"Time taken: {time.time() - start}s")
    input()
