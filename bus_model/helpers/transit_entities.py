import logging
import helpers.gtfsr as gtfsr
import os
import requests

from collections import defaultdict
from datetime import datetime, timedelta
from math import ceil
from time import time

logging.basicConfig(level=logging.INFO)

def timestamp_to_HM(timestamp: int) -> str:
    """Converts a Unix timestamp to HH:MM format."""
    return datetime.fromtimestamp(timestamp).strftime("%H:%M")

class Bus:
    """A class to represent a bus and its relevant information."""
    _all: dict[str, 'Bus'] = {}

    STYLE_NULL = 0
    STYLE_COACH = 1
    STYLE_DOUBLE_DECKER = 2
    STYLE_MINIBUS = 3    
    STYLE_TRAM = 4
    STYLE_ARTICULATED = 5

    FUEL_NULL = 0
    FUEL_DIESEL = 1
    FUEL_ELECTRIC = 2
    FUEL_HYBRID = 3
    FUEL_GAS = 4
    FUEL_HYDROGEN = 5


    def __init__(self, slug: str):
        self._all[slug] = self
        self.slug = slug
        self.time_lat_lon = []
        self.latest_timestamp = 0
        self.latest_trip = None
        self.latest_route = None
        self.lat = None
        self.lon = None
        self.rotation = 0
    
    def set_details(self, reg: str, fleet_code: str, name: str, style: int, fuel: int, double_decker: bool, coach: bool, electric: bool, livery: dict, withdrawn: bool, special_features: str):
        """Sets the details of the bus."""
        self.reg = reg
        self.fleet_code = fleet_code
        self.name = name
        self.style = style
        self.fuel = fuel
        self.double_decker = double_decker
        self.coach = coach
        self.electric = electric
        self.livery = livery
        self.withdrawn = withdrawn
        self.special_features = special_features
    
    def add_live_update(self, trip_id: str, route_id: str, timestamp: int, latitude: float, longitude: float, start_time: str, start_date: str, schedule_relationship: str, direction_id: bool):
        """Populates the object with the latest live bus data."""
        if self.latest_trip != trip_id:
            self.time_lat_lon = []
            self.latest_trip = trip_id
            self.latest_route = route_id
            self.start_time = start_time
            self.start_date = start_date
        if (tup := (timestamp, latitude, longitude)) not in self.time_lat_lon:
            self.time_lat_lon.append(tup)
            self.latest_timestamp = self.time_lat_lon[-1][0]   # Unix timestamp
            self.lat = self.time_lat_lon[-1][1]
            self.lon = self.time_lat_lon[-1][2]
            self.schedule_relationship = schedule_relationship
            self.direction = direction_id
            shape_id = Trip._all[trip_id].shape.shape_id
            points = gtfsr.StaticGTFSR.nearest_points(self.lat, self.lon, shape_id)
            if points:
                p1, p2 = points
                lat1, lon1, lat2, lon2 = p1[1], p1[2], p2[1], p2[2]
                angle = gtfsr.StaticGTFSR.calculate_bearing(lat1, lon1, lat2, lon2)
                self.rotation = angle
            
            try:
                uri = os.getenv("INFERENCE_URI")
                response = requests.post(uri + "/predictions", json=self.inference_data_supply())
                json_data = response.json()
                if not json_data.get("error", None):
                    delay = json_data.get("delay", 0)   #   Delay in seconds
                    predictions = {}
                    all_stops = json_data.get("stops", {})
                    if all_stops:
                        for stop in all_stops:
                            stop_id = stop.get("stop_id", "")
                            time_type = stop.get("type", "")
                            schedule_arr_time = stop.get("scheduled_arrival_time", 0)
                            arrival_time  = stop.get("arrival_time", 0)
                            if time_type == "Scheduled":
                                arrival_time = schedule_arr_time + delay
                            predictions[stop_id] = {"arrival_time": arrival_time,
                                                    "type": time_type,
                                                    "delay": delay, 
                                                    "schedule_arrival_time": schedule_arr_time}
                        Trip._all[trip_id].predicted_stop_visit_times = predictions
                        #print(f"Added data to {trip_id} {predictions}")
                else:
                    ... #print(f"Error: {json_data.get('error')}", end=" ")

            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch inference data: {e}")

        trip = Trip._all.get(trip_id, None)
        if trip:
            trip.latest_bus = self.slug
    
    def inference_data_supply(self) -> dict:
        """Returns JSON data in the correct format for the model."""
        return {
            "trip_id": self.latest_trip,
            "start_time": self.start_time,
            "start_date": self.start_date,
            "schedule_relationship": self.schedule_relationship,
            "route_id": self.latest_route,
            "direction_id": self.direction,
            "vehicle_updates": [
                {"latitude": tll[1], "longitude": tll[2], "timestamp": tll[0]} for tll in self.time_lat_lon
            ]
            }
    
    def get_info(self) -> dict[str, str]:
        """Returns the bus's information in a dictionary."""
        return {
            "bus_id": self.slug,
            "reg": self.reg,
            "fleet_code": self.fleet_code,
            "vehicle_details": {
                "name": self.name,
                "style": self.style,
                "fuel": self.fuel,
                "double_decker": self.double_decker,
                "coach": self.coach,
                "electric": self.electric
                },
            "livery": self.livery,
            "withdrawn": self.withdrawn,
            "special_features": self.special_features,
            "trip_id": self.latest_trip,
            "route_id": self.latest_route,
            "timestamp": self.latest_timestamp,
            "latitude": self.lat,
            "longitude": self.lon
        }
    
    @classmethod
    def get_all_buses(cls) -> list[dict]:
        """Returns a list of all buses."""
        buses = []
        threshold_time = time() - 600   # 10 mins ago
        for bus in cls._all.values():
            if bus.latest_timestamp > threshold_time:
                trip = Trip._all.get(bus.latest_trip, None)
                route = Route._all.get(bus.latest_route, None)
                if trip and route:
                    data = {"id" : bus.slug,
                            "route" : route.route_short_name,
                            "headsign" : trip.trip_headsign,
                            "direction" : bus.rotation,
                            "lat" : bus.lat,
                            "lon" : bus.lon,
                            "timestamp" : timestamp_to_HM(bus.latest_timestamp)
                            }
                    buses.append(data)
        print(f"Active buses/total buses: {len(buses)}/{len(cls._all)}")
        if len(buses) == 0:
            print("Likely to be missing live bus data.")
        return buses
            


class Stop:
    """A class to represent a bus stop and its relevant information."""
    _all: dict[str, "Stop"] = {}

    def __init__(self, stop_id: str, stop_code: str, stop_name: str, stop_lat: float, stop_lon: float):
        self._all[stop_id] = self
        self.stop_id = stop_id
        self.stop_code = stop_code
        self.stop_name = stop_name
        self.stop_lat = stop_lat
        self.stop_lon = stop_lon
        self.bus_visits: list[str] = [] # List of BusStopVisit ids at this stop
        self.routes: set[str] = set()
        self.trips: set[str] = set()
        self.rotation = 0
    
    def get_info(self) -> dict[str, str]:
        """Returns the stop's information in a dictionary."""
        return {
            "id": self.stop_id,
            "code": self.stop_code,
            "name": self.stop_name,
            "lat": self.stop_lat,
            "lon": self.stop_lon,
            "direction": self.rotation,
        }
    
    def get_timetables(self, date: datetime) -> list[dict]:
        """Fetches the timestamps of all trip visits on the given date."""
        date_str = date.date().strftime("%Y-%m-%d")
        visits: list = []
        for trip_id in self.trips:
            trip = Trip._all.get(trip_id, None)
            if trip:        # Current trip goes through stop
                if trip.predicted_stop_visit_times:
                    stop_info_dict = trip.predicted_stop_visit_times.get(self.stop_id, {})
                    if stop_info_dict and trip.latest_bus:
                        if stop_info_dict.get("type", "Scheduled") == "Scheduled":
                            schedule_time = trip.get_bus_stop_schedule_arrival_time(self.stop_id)
                            arr_time = timestamp_to_HM(schedule_time + stop_info_dict.get("delay", 0))
                            schedule_time = timestamp_to_HM(schedule_time)
                            delay = stop_info_dict.get("delay", 0)
                            arrival_time =  f"{arr_time} ({schedule_time} + {delay})"
                        else:
                            arrival_time = f"{timestamp_to_HM(stop_info_dict.get('arrival_time', 0))}"
                        visits.append({
                            "id": trip.latest_bus,
                            "route": trip.route.route_short_name,
                            "headsign": trip.trip_headsign,
                            "arrival": arrival_time,
                        })
                else: # Missing predictions
                    timestamps = trip.get_schedule_times().get(date_str, {})
                    visit_time = timestamps.get(self.stop_id, None)
                    if visit_time and trip.latest_bus:
                        visits.append({
                            "id": trip.latest_bus,
                            "route": trip.route.route_short_name,
                            "headsign": trip.trip_headsign,
                            "arrival": timestamp_to_HM(visit_time),
                            #"current_trip": True,
                        })
                    elif visit_time:    # Next trip goes through stop
                        trips = trip.get_trips_in_block(date)
                        prev_trips = [t for t in sorted(trips, key=lambda t: BusStopVisit._all[t.bus_stop_times[0]].arrival_time) if BusStopVisit._all[t.bus_stop_times[0]].arrival_time < BusStopVisit._all[trip.bus_stop_times[0]].arrival_time]
                        if len(prev_trips) > 0 and prev_trips[-1].latest_bus:
                            if prev_trips[-1].predicted_stop_visit_times:
                                stop_info_dict = prev_trips[-1].predicted_stop_visit_times.get(self.stop_id, {})
                                if stop_info_dict:
                                    delay = stop_info_dict.get("delay", 0)
                                    schedule_time = prev_trips[-1].get_bus_stop_schedule_arrival_time(self.stop_id)
                                    arr_time = timestamp_to_HM(schedule_time + delay)
                                    schedule_time = timestamp_to_HM(schedule_time)   
                                    arrival_time = f"{arr_time} ({schedule_time}+{ceil(delay//60)})"
                                    visits.append({
                                        "id": prev_trips[-1].latest_bus,
                                        "route": prev_trips[-1].route.route_short_name,
                                        "headsign": prev_trips[-1].trip_headsign,
                                        "arrival": arrival_time,
                                        #"current_trip": False,
                                    })
                            else:
                                visits.append({
                                    "id": prev_trips[-1].latest_bus,
                                    "route": trip.route.route_short_name,
                                    "headsign": trip.trip_headsign,
                                    "arrival": timestamp_to_HM(visit_time),
                                    #"current_trip": False, 
                                })
        return sorted([v for v in visits if v["arrival"] > timestamp_to_HM(datetime.now().timestamp())], key=lambda x: x["arrival"])


class Route:
    """A class to represent a bus route and its relevant information."""
    _all: dict[str, 'Route'] = {}

    def __init__(self, route_id: str, agency_id: str, route_short_name: str, route_long_name: str, route_type: int):
        self._all[route_id] = self
        self.route_id = route_id
        self.agency = Agency._all[agency_id]
        self.route_short_name = route_short_name
        self.route_long_name = route_long_name
        self.route_type = route_type
        self.all_trips: list[str] = []
        self.all_stops: set[str] = set()

    def get_info(self) -> dict[str, str]:
        """Returns the route's information in a dictionary."""
        return {
            "route_id": self.route_id,
            "agency_id": self.agency.agency_id,
            "route_short_name": self.route_short_name,
            "route_long_name": self.route_long_name,
            "route_type": self.route_type
        }
    
    def add_stop(self, stop_id: str):
        """Adds a stop to the route's list of stops."""
        self.all_stops.add(stop_id)
    
    def enumerate_stops(self):
        for trip_id in self.all_trips:
            for bus_stop_visit_id in Trip._all[trip_id].bus_stop_times:
                self.add_stop(BusStopVisit._all[bus_stop_visit_id].stop.stop_id)
        for stop_id in self.all_stops:
            Stop._all[stop_id].routes.add(self.route_id)
    
class Trip:
    """A class to represent a trip and its relevant information."""
    _all: dict[str, "Trip"] = {}

    def __init__(self, trip_id: str, route_id: str, service_id: str, shape_id: str, trip_headsign: str, trip_short_name: str, direction: bool, block_id: str):
        self._all[trip_id] = self
        self.trip_id = trip_id
        self.route = Route._all[route_id]
        self.service = Service._all[service_id]
        self.shape = Shape._all.get(shape_id, None)
        self.trip_headsign = trip_headsign
        self.trip_short_name = trip_short_name
        self.direction = direction
        self.block_id = block_id
        self.bus_stop_times: list[str] = []
        self.stop_id_stop_seq: dict[str, int] = {}
        self.latest_bus: str = None
        self.predicted_stop_visit_times = {}  #  From Inference container

        self.route.all_trips.append(self.trip_id)
    
    def get_info(self) -> dict[str, str]:
        """Returns the trip's information in a dictionary."""
        return {
            "trip_id": self.trip_id,
            "route_id": self.route.route_id,
            "service_id": self.service.service_id,
            "shape_id": self.shape.shape_id,
            "trip_headsign": self.trip_headsign,
            "trip_short_name": self.trip_short_name,
            "direction": self.direction,
            "block_id": self.block_id
        }
    
    def get_bus_stop_schedule_arrival_time(self, stop_id: str) -> int:
        """Returns the BusStopVisit object for the given stop ID."""
        for visit_ids in self.bus_stop_times:
            visit = BusStopVisit._all[visit_ids]
            if visit.stop.stop_id == stop_id:
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                return int(today.timestamp()) + int(visit.arrival_time.total_seconds())
        raise KeyError("Stop not found in trip.")
        return 0

    def sort_bus_stop_times(self):
        self.bus_stop_times = sorted(self.bus_stop_times, key=lambda x: BusStopVisit._all[x].stop_sequence)
    
    def get_schedule_times(self) -> dict[str, dict[str, int]]:
        """Returns a dict of all timestamps for the trip for each day.""" # this sort of should be returning something else, maybe combine into stop -> routes -> trips -> times
        all_timestamps: defaultdict = defaultdict(dict)
        current_date = self.service.start_date
        while current_date <= self.service.end_date:
            day = current_date.weekday()
            if self.service.schedule_days[day] and current_date not in self.service.cancelled_exceptions:
                timestamps: dict[str, int] = {}
                for visit in self.bus_stop_times:
                    bus_stop_time: BusStopVisit = BusStopVisit._all[visit]
                    new_timestamp = int(current_date.timestamp()) + int(bus_stop_time.arrival_time.total_seconds())
                    timestamps[bus_stop_time.stop.stop_id] = new_timestamp
                all_timestamps[current_date.date().strftime("%Y-%m-%d")] = timestamps
            current_date += timedelta(days=1)
        
        for exception in self.service.extra_exceptions:
            if exception not in self.service.cancelled_exceptions:
                timestamps = all_timestamps[exception.date().strftime("%Y-%m-%d")]
                for visit in self.bus_stop_times:
                    bus_stop_time: BusStopVisit = BusStopVisit._all[visit]
                    new_timestamp = int(exception.timestamp()) + int(bus_stop_time.arrival_time.total_seconds())
                    timestamps[bus_stop_time.stop.stop_id] = new_timestamp
                all_timestamps[exception.date().strftime("%Y-%m-%d")] = timestamps
        return all_timestamps

    def get_trips_in_block(self, date: datetime, subsequent_only: bool = False) -> list['Trip']:
        potential_trips = []
        for trip_id in self._all:
            trip = self._all[trip_id]
            if trip.block_id == self.block_id:
                if trip.service.check_in_range(date): # check if it is in date range
                    potential_trips.append(trip)
        return [t for t in sorted(potential_trips, key=lambda t: BusStopVisit._all[t.bus_stop_times[0]].arrival_time) if not subsequent_only or BusStopVisit._all[t.bus_stop_times[0]].arrival_time > BusStopVisit._all[self.bus_stop_times[0]].arrival_time]

    def get_start_time(self) -> datetime:
        """Returns the datetime object for the start of the trip."""
        return datetime.fromtimestamp(int(self.service.start_date.timestamp()) + int(BusStopVisit._all[self.bus_stop_times[0]].arrival_time.total_seconds()))
    
    @classmethod
    def filter_by_routes(cls, route_ids: list|str) -> list[dict[str, str]]:
        """Filters the list of all trips by specified route IDs."""
        if isinstance(route_ids, str):
            route_ids = [route_ids]
        return [trip.get_info() for trip in cls._all.values() if trip.route.route_id in route_ids]
    
class BusStopVisit:
    """A class to record the time of a stop in a trip."""
    _all: dict[str, 'BusStopVisit'] = {}

    def __init__(self, trip_id: str, stop_id: str, arrival_time: timedelta, departure_time: timedelta, stop_sequence: int, stop_headsign: str, pickup_type: bool, drop_off_type: bool, timepoint: bool):
        self.trip = Trip._all[trip_id]
        self.stop = Stop._all[stop_id]
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.stop_sequence = stop_sequence
        self.stop_headsign = stop_headsign
        self.pickup_type = pickup_type
        self.drop_off_type = drop_off_type
        self.timepoint_type = timepoint
        self._id = f"{trip_id}_{stop_id}_{stop_sequence}"
        self._all[self._id] = self

        self.stop.bus_visits.append(self._id)
        self.trip.bus_stop_times.append(self._id)
        self.stop.trips.add(self.trip.trip_id)
        self.trip.stop_id_stop_seq[stop_sequence] = stop_id


class Service:
    """Represents a weekly schedule through a set of booleans"""
    _all: dict[str, 'Service'] = {}
    ADDED_EXCEPTION = 1
    REMOVED_EXCEPTION = 2

    def __init__(self, service_id: str, monday: bool, tuesday: bool, wednesday: bool, thursday: bool, friday: bool, saturday: bool, sunday: bool, start_date: datetime, end_date: datetime):
        self._all[service_id] = self
        self.service_id = service_id
        self.schedule_days = [monday, tuesday, wednesday, thursday, friday, saturday, sunday]
        self.start_date = start_date
        self.end_date = end_date + timedelta(days=1)    # inclusive, this brings it to the end of the day
        self.extra_exceptions: list[datetime] = []
        self.cancelled_exceptions: list[datetime] = []
    
    def add_exception(self, date: datetime, exception_type: int):
        """Records an exception to the schedule, to be parsed on schedule generation in a different method."""
        if exception_type == self.ADDED_EXCEPTION:
            self.extra_exceptions.append(date)
        elif exception_type == self.REMOVED_EXCEPTION:
            self.cancelled_exceptions.append(date)
        else:
            raise ValueError("X exception type.")
    
    def check_in_range(self, date: datetime) -> bool:
        """Checks if the given date is within the service's date range and is on the right day of week."""
        return self.start_date <= date <= self.end_date and self.schedule_days[date.weekday()]

class Agency:
    """A class to represent a bus agency and its relevant information."""
    _all: dict[str, 'Agency'] = {}

    def __init__(self, agency_id: str, agency_name: str):
        self._all[agency_id] = self
        self.agency_id = agency_id
        self.agency_name = agency_name

    def get_info(self) -> dict[str, str]:
        """Returns the agency's ID and name."""
        return {
            "agency_id": self.agency_id,
            "agency_name": self.agency_name
        }

class Shape:
    """A class representing a trip's journey via sequence of coordinates."""
    _all: dict[str, 'Shape'] = {}

    def __init__(self, shape_id: str):
        self._all[shape_id] = self
        self.shape_id = shape_id
        self.shape_coords: list[Point] = []
    
    def add_point(self, lat: float, lon: float, sequence: int, dist_traveled: float):
        """Adds a point to the shape."""
        self.shape_coords.append(Point(lat, lon, sequence, dist_traveled))

    def get_info(self) -> list[dict[str, float]]:
        """Returns a list of the coordinates of the shape."""
        return [point.get_info() for point in self.shape_coords]

class Point:
    """A class representing a latitude and longitude coordinate."""

    def __init__(self, lat: float, lon: float, sequence: int, dist_traveled: float):
        self.lat = lat
        self.lon = lon
        self.sequence = sequence
        self.dist_traveled = dist_traveled

    def get_info(self) -> dict[str, float]:
        """Returns the latitude and longitude of the point."""
        return {
            "lat": self.lat,
            "lon": self.lon,
            "sequence": self.sequence,
            "dist_traveled": self.dist_traveled
        }


def search_attribute(cls, attribute: str, value: str) -> list:
    """Fetches all instances of a class with a certain attribute value."""
    return [instance for instance in cls._all.values() if getattr(instance, attribute) == value]
