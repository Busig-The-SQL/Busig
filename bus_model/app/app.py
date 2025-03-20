import bus_model
import datetime
import os
import requests
import subprocess
import time

from flask import Flask, g, abort, jsonify, request
from bus_model.app.gtfsr import GTFSR, StaticGTFSR, BustimesAPI
from bus_model.GTFS_Static.db_funcs import get_route_id_to_name_dict
from dotenv import load_dotenv
from math import ceil

subprocess.Popen(["service", "cron", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

load_dotenv()
training_uri = os.getenv("TRAINING_URI")

app = Flask(__name__)
load_before = time.time()
StaticGTFSR.load_all_files()


@app.before_request
def before_request():
    """Timing Debug"""
    g.start_time = time.time()

@app.teardown_request
def teardown_request(execution=None):
    """Timing Debug"""
    diff = time.time() - g.start_time
    print(f"Request took {diff} seconds")

@app.route("/", methods=["GET"])
def test():
    return {"message" : "Hello, World!"}

@app.route("/v1/vehicle")
def vehicles():
    """Directly fetches and returns the live vehicles data."""
    return GTFSR.fetch_vehicles()

@app.route("/v1/stops", methods=["GET"])
def stops():  
    """Fetches and returns information of all stops."""
    return [stop.get_info() for stop in bus_model.Stop._all.values()]

@app.route("/v1/stop/<string:stop_id>", methods=["GET"])
def stop(stop_id: str):
    """Fetches information for a specific stop based on stop_id or stop_code."""
    if len(stop_id) > 8:    # stop_id
        return generic_get_or_404(bus_model.Stop, stop_id)
    else:   # stop_code
        return bus_model.search_attribute(bus_model.Stop, "stop_code", stop_id)[0].get_info()

@app.route("/v1/stop/arrivals/<string:stop_id>", methods=["GET"])
def stop_arrivals(stop_id: str):
    """Fetches all bus arrivals for a specific stop"""
    stop = bus_model.Stop._all.get(stop_id, None)
    if stop:
        return stop.get_timetables(datetime.datetime.now())    # doesn't really work near midnight rn
    return abort(404)

@app.route("/v1/trip/<string:trip_id>", methods=["GET"])
def trips(trip_id: str):    
    """Fetches information for a specific trip based on trip_id."""
    return generic_get_or_404(bus_model.Trip, trip_id)

@app.route("/v1/agency/<string:agency_id>", methods=["GET"])
def agency(agency_id: str):
    """Fetches information for a specific agency based on agency_id."""
    return generic_get_or_404(bus_model.Agency, agency_id)

@app.route("/v1/route", methods=["GET"])
def routes():
    """Fetches a list of all routes."""
    return [{"name": route.route_short_name, "stop_ids" : list(route.all_stops)} for route in bus_model.Route._all.values()]

@app.route("/v1/route/<string:route_id>", methods=["GET"])
def route(route_id: str):
    """Fetches information for a specific route based on route_id."""
    return generic_get_or_404(bus_model.Route, route_id)

@app.route("/v1/route/search/<string:route_name>", methods=["GET"])
def route_search(route_name: str):
    """Fetches all routes that match the route_name keyword."""
    return [route.get_info() for route in bus_model.Route._all.values() if route_name in route.route_short_name]

@app.route("/v1/shape/<string:shape_id>", methods=["GET"])
def shape(shape_id: str):
    """Fetches information for a specific shape based on shape_id."""
    return generic_get_or_404(bus_model.Shape, shape_id)

@app.route("/v1/bus/<string:bus_id>", methods=["GET"])
def bus(bus_id: str):
    """Fetches information for a specific bus based on bus_id."""
    all_stops: list = []
    bus_obj = bus_model.Bus._all.get(bus_id, None)
    if bus_obj:
        trip = bus_model.Trip._all.get(bus_obj.latest_trip, None)
        if trip:
            if trip.predicted_stop_visit_times:
                stop_info_dicts = trip.predicted_stop_visit_times
                print("Predictions", trip.trip_id, stop_info_dicts)
                delay_t = None
                for stop_id, stop_dict in stop_info_dicts.items():
                    delay_t = stop_dict.get("delay", 0)
                    stop = bus_model.Stop._all.get(stop_id, None)
                    if stop_dict.get("type", "Scheduled") == "Scheduled":
                        schedule_time = trip.get_bus_stop_schedule_arrival_time(stop_id)
                        arr_time = bus_model.timestamp_to_HM(schedule_time + stop_dict.get("delay", 0))
                        schedule_time = bus_model.timestamp_to_HM(schedule_time)
                        delay = stop_dict.get("delay", 0)
                        arrival_time = f"{arr_time} ({schedule_time} + {ceil(delay//60)})"
                    else:
                        arrival_time = bus_model.timestamp_to_HM(stop_dict.get("arrival_time", 0))
                    data = {
                            "id": stop.stop_id,
                            "code": stop.stop_code,
                            "name": stop.stop_name,
                            "arrival": arrival_time + " PREDICTION",
                            #"current_trip": True,
                            }
                    all_stops.append(data)
                day = trip.get_start_time()
                other_trips = trip.get_trips_in_block(day, subsequent_only=True)[:1]    # Next n trips
                for t in other_trips:
                    stop_timestamps = t.get_schedule_times()
                    for stop_id, timestamp in stop_timestamps.get(day.strftime("%Y-%m-%d"), {}).items():
                        stop = bus_model.Stop._all.get(stop_id, None)
                        data = {
                                "id": stop.stop_id,
                                "code": stop.stop_code,
                                "name": stop.stop_name,
                                "arrival": bus_model.timestamp_to_HM(timestamp + delay_t)# + " DELAY, next",
                                #"current_trip": False,
                                }
                        all_stops.append(data) 
            else:   # Missing predictions
                print("No predictions", trip.trip_id)
                stop_timestamps = trip.get_schedule_times()
                day = trip.get_start_time()
                for stop_id, timestamp in stop_timestamps.get(day.strftime("%Y-%m-%d"), {}).items():
                    stop = bus_model.Stop._all.get(stop_id, None)
                    data = {
                            "id": stop.stop_id,
                            "code": stop.stop_code,
                            "name": stop.stop_name,
                            "arrival": bus_model.timestamp_to_HM(timestamp)# + " SCHEDULE",
                            #"current_trip": True,
                            }
                    all_stops.append(data)
                other_trips = trip.get_trips_in_block(day, subsequent_only=True)[:1]    # Next n trips
                for t in other_trips:
                    stop_timestamps = t.get_schedule_times()
                    for stop_id, timestamp in stop_timestamps.get(day.strftime("%Y-%m-%d"), {}).items():
                        stop = bus_model.Stop._all.get(stop_id, None)
                        data = {
                                "id": stop.stop_id,
                                "code": stop.stop_code,
                                "name": stop.stop_name,
                                "arrival": bus_model.timestamp_to_HM(timestamp)# + " SCHEDULE, next",
                                #"current_trip": False,
                                }
                        all_stops.append(data) 

            return all_stops
    return abort(404)


@app.route("/v1/bus", methods=["GET"])
def buses():
    """Fetches information for all buses."""
    return bus_model.Bus.get_all_buses()

@app.route("/v1/route_id_to_name", methods=["GET"])
def route_id_to_name():
    """Fetches a mapping between route_id to route names"""
    return jsonify(get_route_id_to_name_dict())

@app.route("/v1/update_realtime", methods=["GET"])
def update_realtime():
    """Takes the fetched data and populates the model."""
    print("Triggering realtime update")
    data = GTFSR.fetch_vehicles()
    # This line breaks, because GTFSR.fetch_vehicles() can return None
    data = GTFSR.fetch_vehicles()
    entities = data.get("entity", [])
    if entities:
        for entity in entities:
            try:
                trip_id = entity["vehicle"]["trip"]["trip_id"]
                if trip_id in bus_model.Trip._all:
                    route_id = entity["vehicle"]["trip"]["route_id"]
                    vehicle_id = entity["vehicle"]["vehicle"]["id"]
                    timestamp = int(entity["vehicle"]["timestamp"])
                    latitude = float(entity["vehicle"]["position"]["latitude"])
                    longitude = float(entity["vehicle"]["position"]["longitude"])
                    start_time = entity["vehicle"]["trip"]["start_time"]
                    start_date = entity["vehicle"]["trip"]["start_date"]
                    schedule_relationship = entity["vehicle"]["trip"]["schedule_relationship"]
                    direction_id = entity["vehicle"]["trip"]["direction_id"]
                    bus = bus_model.Bus._all.get(vehicle_id, None)
                    if bus:
                        bus.add_live_update(trip_id=trip_id, route_id=route_id, timestamp=timestamp, latitude=latitude, longitude=longitude, start_time=start_time, start_date=start_date, schedule_relationship=schedule_relationship, direction_id=direction_id)
            except KeyError as e:
                print(f"KeyError: {e}")
                continue
    try:
        requests.put(training_uri + "/trips", data=data)
    except requests.exceptions.RequestException as e:
        print(f"Failed to send data to training container: {e}")
    return "Success"

@app.route("/v1/update_static", methods=["GET"])
def update_static():
    """Takes the fetched data and populates the model."""
    StaticGTFSR.load_all_files()
    return "Success"

@app.route("/v1/update_bus", methods=["GET"])
def update_bus():
    """Updates the bus data."""
    data = BustimesAPI.fetch_vehicles()
    if data:
        for bus in data:
            cleaned_slug = bus["slug"].replace("ie-", "")
            bus_obj = bus_model.Bus(slug=cleaned_slug) if cleaned_slug not in bus_model.Bus._all else bus_model.Bus._all[cleaned_slug]
            v_type = bus.get("vehicle_type") or {}
            bus_obj.set_details(
                reg=bus.get("reg", ""),
                fleet_code=bus.get("fleet_code", ""),
                name=v_type.get("name", ""),
                style=v_type.get("style", ""),
                fuel=v_type.get("fuel", ""),
                double_decker=v_type.get("double_decker", ""),
                coach=v_type.get("coach", ""),
                electric=v_type.get("electric", ""),
                livery=bus.get("livery", {}),
                withdrawn=bus.get("withdrawn", ""),
                special_features=bus.get("special_features", "")
            )
        # Make PUT req to AI
        return "Success"
    return "Failed"

@app.errorhandler(500)
def internal_server_error(e) -> dict:
    """500 Error Handler"""
    return {"error_code": 500, "error_message": "Internal Server Error"}, 500

@app.errorhandler(404)
def page_not_found(e) -> dict:
    """404 Error Handler"""
    return {"error_code": 404, "error_message": "Page not found"}, 404

def generic_get_or_404(cls, id_: str) -> dict:
    """Generic function to get info dict of the classes else raise a 404 error"""
    if obj := cls._all.get(id_, None):
        return obj.get_info()
    else:
        abort(404)

update_bus()                    # Update the bus data on startup
update_realtime()               # Update the realtime data on startup
print(f"Loaded in {time.time() - load_before} seconds")
print("Loaded")
