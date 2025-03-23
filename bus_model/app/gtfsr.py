import bus_model.app.transit_entities as model
import datetime
import math
import os
import requests
import subprocess
import time

from dotenv import load_dotenv
from bus_model.GTFS_Static.db_connection import create_connection, close_connection


load_dotenv()

def manage_read_only_connection(func):
    def wrapper(*args, **kwargs):
        conn = create_connection()
        cursor = conn.cursor()
        data = None
        try:
            data = func(cursor, *args, **kwargs)
        finally:
            close_connection(conn)
            return data
    return wrapper

class BustimesAPI:
    base_url = "https://bustimes.org/api/vehicles?limit="
    limit = "70000"

    @classmethod
    def fetch_vehicles(self) -> dict:
        """Fetches and filters all the vehicles from the Bustimes API."""
        url = self.base_url + self.limit
        try:
            data = requests.get(url)
            data = data.json()
        except Exception as e:
            print("Non-fatal Error:", e)
            print(data.text)
            return None
        vehicles: list[dict] = data.get("results", [])
        if vehicles:
            filtered = [vehicle for vehicle in vehicles if vehicle.get("slug", "").startswith("ie-")]
            return filtered
        return None

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
    date_format = "%Y%m%d"
    time_format = "%H:%M:%S"


    @classmethod
    @manage_read_only_connection
    def get_routes(cursor, _):
        query = """SELECT * FROM ROUTES"""
        cursor.execute(query)
        res = cursor.fetchall()
        for row in res:
            model.Route(route_id=row[0], agency_id=row[1], route_short_name=row[2], route_long_name=row[3], route_type=row[4])

    @classmethod
    @manage_read_only_connection
    def get_stops(cursor, _):
        query = """SELECT * FROM STOPS"""
        cursor.execute(query)
        res = cursor.fetchall()
        type_coerce = lambda x: str(int(float(x)))
        for row in res:
            model.Stop(stop_id=row[0], stop_code=type_coerce(row[1]), stop_name=row[2], stop_lat=row[3], stop_lon=row[4])

    @classmethod
    @manage_read_only_connection
    def get_agencies(cursor, _):
        query = """SELECT * FROM AGENCY"""
        cursor.execute(query)
        res = cursor.fetchall()
        for row in res:
            model.Agency(agency_id=row[0], agency_name=row[1])

    @classmethod
    @manage_read_only_connection
    def get_calendar(cursor, cls):
        query = """SELECT * FROM CALENDAR"""
        cursor.execute(query)
        res = cursor.fetchall()
        for row in res:
            start_date = datetime.datetime.strptime(row[8], cls.date_format)
            end_date = datetime.datetime.strptime(row[9], cls.date_format)
            model.Service(service_id=row[0], monday=row[1], tuesday=row[2], wednesday=row[3], thursday=row[4], friday=row[5], saturday=row[6], sunday=row[7], start_date=start_date, end_date=end_date)

    @classmethod
    @manage_read_only_connection
    def get_calendar_dates(cursor, cls):
        query = """SELECT * FROM CALENDAR_DATES"""
        cursor.execute(query)
        res = cursor.fetchall()
        for row in res:
            date = datetime.datetime.strptime(row[1], cls.date_format)
            service = model.Service._all[row[0]]
            service.add_exception(date, int(row[2]))

    @classmethod
    @manage_read_only_connection
    def get_shapes(cursor, _):
        query = """SELECT * FROM SHAPES
                   ORDER BY shape_pt_sequence"""
        cursor.execute(query)
        res = cursor.fetchall()
        for row in res:
            shape_id = row[0]
            if shape_id not in model.Shape._all:
                shape = model.Shape(shape_id)
            else:
                shape = model.Shape._all[shape_id]
            shape.add_point(lat=row[1], lon=row[2], sequence=row[3], dist_traveled=row[4])

    @classmethod
    @manage_read_only_connection
    def get_trips(cursor, _):
        query = """SELECT * FROM TRIPS"""
        cursor.execute(query)
        res = cursor.fetchall()
        for row in res:
            model.Trip(route_id=row[0], service_id=row[1], trip_id=row[2], trip_headsign=row[3], trip_short_name=row[4], direction=row[5], block_id=row[6], shape_id=row[7])

    @classmethod
    @manage_read_only_connection
    def get_stop_times(cursor, _):
        query = """SELECT * FROM STOP_TIMES"""
        cursor.execute(query)
        res = cursor.fetchall()
        for row in res:
            h, m, s = map(int, row[1].split(":"))
            arrival_delta = datetime.timedelta(hours=h, minutes=m, seconds=s)
            h, m, s = map(int, row[2].split(":"))
            departure_delta = datetime.timedelta(hours=h, minutes=m, seconds=s)
            headsign = row[5] if row[5] != "nan" else None
            model.BusStopVisit(trip_id=row[0], arrival_time=arrival_delta, departure_time=departure_delta, stop_id=row[3], stop_sequence=row[4], stop_headsign=headsign, pickup_type=row[6], drop_off_type=row[7], timepoint=row[8])
    
    @classmethod
    def calculate_bearing(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> int:
        """
        Calculates the bearing/angle between two lat/lon points relative to North.
        """
        lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        
        delta_lon = lon2 - lon1
        
        x = math.sin(delta_lon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon))
        
        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = int((initial_bearing + 360) % 360)
        return compass_bearing


    @classmethod
    @manage_read_only_connection
    def nearest_points(cursor, cls, lat: float, lon: float, shape_id: str) -> list[tuple]:
        query = """
                    WITH sh1 AS (
                        SELECT shape_pt_sequence AS stop_seq, shape_pt_lat AS lat, shape_pt_lon AS lon, shape_dist_traveled, shape_id
                        FROM shapes AS sh1
                        WHERE shape_id = %s
                        ORDER BY POWER(shape_pt_lat - %s, 2) + POWER(shape_pt_lon - %s, 2)
                        LIMIT 1
                        ),
                    sh2 AS (
                        SELECT shape_pt_sequence AS stop_seq, shape_pt_lat AS lat, shape_pt_lon AS lon
                        FROM shapes AS sh2
                        JOIN sh1 AS sh1 ON sh2.shape_id = sh1.shape_id
                        WHERE sh2.shape_id = %s
                            AND (sh2.shape_dist_traveled <= (sh1.shape_dist_traveled - 5) OR sh2.shape_dist_traveled >= (sh1.shape_dist_traveled + 5))
                        ORDER BY abs(sh2.shape_dist_traveled - sh1.shape_dist_traveled) ASC
                        LIMIT 1
                    )
                    SELECT * FROM (
                        SELECT stop_seq, lat, lon FROM sh1
                        UNION ALL
                        SELECT stop_seq, lat, lon FROM sh2
                   ) as combined_results
                   ORDER BY stop_seq ASC;
                   """
        cursor.execute(query, (shape_id, lat, lon, shape_id))
        if res := cursor.fetchall():
            return [(seq, lat, lon) for seq, lat, lon in res]
        print("No res", lat, lon)
        return None

    @classmethod
    @manage_read_only_connection
    def post_loading_calculations(cursor, cls):
        # These are basically "joins" of SQL tables
        for trip in model.Trip._all.values():
            trip.sort_bus_stop_times()
        for route in model.Route._all.values():
            route.enumerate_stops()
        # Get direction
        for stop in model.Stop._all.values():
            stop_lat, stop_lon = stop.stop_lat, stop.stop_lon
            shape_id = model.Trip._all[list(stop.trips)[0]].shape.shape_id
            points = StaticGTFSR.nearest_points(stop_lat, stop_lon, shape_id)
            if points:
                assert len(points) == 2, f"Only {len(points)} points returned."
                p1, p2 = points
                lat1, lon1, lat2, lon2 = p1[1], p1[2], p2[1], p2[2]
                angle = cls.calculate_bearing(lat1, lon1, lat2, lon2)
                stop.rotation = angle              
    
        
    
    @classmethod
    def load_all_files(self):
        t1 = time.time()
        postgres_db_flag_dir = os.getenv("POSTGRES_DB_MADE_DIR")
        file_name = "flag.txt"
        file_path = os.path.join(postgres_db_flag_dir, file_name)

        try:
            if not os.path.exists(file_path):
                process = subprocess.run(["bash", "scripts/update_GTFS_Static.sh"], capture_output=True, text=True) # Create and populate DB
                if process.returncode == 0:
                    with open(file_path, "w") as f: # Only create flag on success
                        f.write("1")
                else:
                    print("Error updating GTFS Static data. Error code:", process.returncode)
        except Exception as e:
            print("Error updating GTFS Static data:", e)

        print(f"GTFS Static data updated in {(t:=time.time()) - t1}s")
        self.get_agencies()
        print(f"Agencies loaded in {(t1:=time.time()) - t}s")
        self.get_calendar()
        print(f"Calendar loaded in {(t:=time.time()) - t1}s")
        self.get_stops()
        print(f"Stops loaded in {(t1:=time.time()) - t}s")
        self.get_shapes()
        print(f"Shapes loaded in {(t:=time.time()) - t1}s")
        self.get_routes()
        print(f"Routes loaded in {(t1:=time.time()) - t}s")
        self.get_calendar_dates()
        print(f"Calendar dates loaded in {(t:=time.time()) - t1}s")
        self.get_trips()
        print(f"Trips loaded in {(t1:=time.time()) - t}s")
        self.get_stop_times()
        print(f"Stop times loaded in {(t:=time.time()) - t1}s")
        self.post_loading_calculations()
        print(f"Post loading calculations completed in {(t1:=time.time()) - t}s")


if __name__ == "__main__": 
    # quick debugging
    start = time.time()
    StaticGTFSR.load_all_files()
    #print("num visits", len(model.Trip._all))
    print(f"Time taken: {time.time() - start}s")
    input()
