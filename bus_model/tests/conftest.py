import datetime
import pytest

from unittest import mock

from app import create_app
from config import TestConfig
from helpers import transit_entities as model
from routes.all_routes import update_realtime


@pytest.fixture()
def app(all_test_objects):
    """Create a Flask application instance for testing."""
    app = create_app(TestConfig)
    with app.app_context():
        yield app


@pytest.fixture()
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture()
def vars():
    """Pseudo global variables for testing values"""
    class Config:
        bus_id = "1000"
        route_id = "4538_90266"
        agency_id = "7778020"
        trip_id = "4538_53871"
        stop_id1 = "8380B245791"
        stop_code1 = "245791"
        stop_id2 = "8380B247991"
        stop_code2 = "247991"
        service_id = "10"
        shape_id = "4538_533"

    return Config


@pytest.fixture()
def bus_instance(vars):
    """Fixture to create a Bus instance."""
    bus = model.Bus(slug=vars.bus_id)
    bus.set_details(
        reg="212-C-12345",
        fleet_code="VWD23",
        name="Volvo B5TL Wright Eclipse Gemini 3",
        style="double decker",
        fuel="diesel",
        double_decker=True,
        coach=False,
        electric=False,
        livery={
            "livery": {
                "id": 3547,
                "name": "Bus Éireann",
                "left": "linear-gradient(#fff 70%,#0000 70%),linear-gradient(-45deg,#fff 20%,#ea1d1a 20% 25%,#fff 25% 30%,#ea1d1a 30% 35%,#fff 35% 40%,#ea1d1a 40%)",
                "right": "linear-gradient(#fff 70%,#0000 70%),linear-gradient(45deg,#fff 20%,#ea1d1a 20% 25%,#fff 25% 30%,#ea1d1a 30% 35%,#fff 35% 40%,#ea1d1a 40%)"
            }
        },
        withdrawn=False,
        special_features=None
    )
    yield bus


@pytest.fixture()
def route_instance(vars, agency_instance):
    """Fixture to create a Route instance. Depends on Agency class existance."""
    route = model.Route(
        route_id=vars.route_id,
        agency_id=vars.agency_id,
        route_short_name="220",
        route_long_name="Ballincollig - Douglas - Carrigaline",
        route_type="3"
    )
    yield route


@pytest.fixture()
def trip_instance(vars, route_instance, shape_filled_instance, service_instance):
    """Fixture to create a Trip instance. Depends on Route, Shape, and Service classes existence."""
    trip = model.Trip(
        trip_id=vars.trip_id,
        route_id=vars.route_id,
        service_id=vars.service_id,
        shape_id=vars.shape_id,
        trip_headsign="Carrigaline",
        trip_short_name="22705-00002-1",
        direction="0",
        block_id="1"
    )
    yield trip


@pytest.fixture()
def stop1_instance(vars):
    stop = model.Stop(
        stop_id=vars.stop_id1,
        stop_code=vars.stop_code1,
        stop_name="IDA Ovens",
        stop_lat=51.876872,
        stop_lon=-8.638645
    )
    yield stop


@pytest.fixture()
def stop2_instance(vars):
    stop = model.Stop(
        stop_id=vars.stop_id2,
        stop_code=vars.stop_code2,
        stop_name="Wood Road",
        stop_lat=51.880502,
        stop_lon=-8.635589
    )
    yield stop


@pytest.fixture()
def agency_instance(vars):
    agency = model.Agency(
        agency_id=vars.agency_id,
        agency_name="Bus Éireann"
    )
    yield agency


@pytest.fixture()
def service_instance(vars):
    service = model.Service(
        service_id=vars.service_id,
        monday=True,
        tuesday=False,
        wednesday=True,
        thursday=True,
        friday=False,
        saturday=True,
        sunday=True,
        start_date=datetime.datetime(2025, 3, 3),
        end_date=datetime.datetime(2025, 9, 21)
    )
    yield service


@pytest.fixture()
def bus_stop_visit1_instance(vars, trip_instance, stop1_instance, stop2_instance):
    """Fixture to create a BusStopVisit instance. Depends on Trip and Stop classes existence."""
    bus_stop_visit = model.BusStopVisit(
        trip_id=vars.trip_id,
        stop_id=vars.stop_id1,
        arrival_time=datetime.timedelta(hours=8, minutes=0),
        departure_time=datetime.timedelta(hours=8, minutes=2),
        stop_sequence=1,
        stop_headsign="Carrigaline",
        pickup_type=0,
        drop_off_type=0,
        timepoint=1,
    )
    yield bus_stop_visit


@pytest.fixture()
def bus_stop_visit2_instance(vars, trip_instance, stop1_instance, stop2_instance):
    """Fixture to create a BusStopVisit instance. Depends on Trip and Stop classes existence."""
    bus_stop_visit = model.BusStopVisit(
        trip_id=vars.trip_id,
        stop_id=vars.stop_id2,
        arrival_time=datetime.timedelta(hours=8, minutes=10),
        departure_time=datetime.timedelta(hours=8, minutes=12),
        stop_sequence=2,
        stop_headsign=None,
        pickup_type=0,
        drop_off_type=0,
        timepoint=1,
    )
    yield bus_stop_visit


@pytest.fixture()
def shape_unfilled_instance(vars):
    shape = model.Shape(
        shape_id=vars.shape_id,
    )
    yield shape


@pytest.fixture()
def shape_filled_instance(vars):
    shape = model.Shape(
        shape_id=vars.shape_id,
    )
    shape.add_point(51.876872, -8.638645, 0, 0)
    shape.add_point(51.880502, -8.635589, 0, 100.2)
    shape.add_point(51.882502, -8.635329, 0, 200.2)
    yield shape


@pytest.fixture(autouse=True)
def all_test_objects(
    bus_instance,
    route_instance,
    trip_instance,
    stop1_instance,
    stop2_instance,
    agency_instance,
    service_instance,
    bus_stop_visit1_instance,
    bus_stop_visit2_instance,
    shape_filled_instance,
):
    """Using this fixture will ensure all test objects exist test process, instead of manually importing each.
       All but shape_unfilled
    """
    route_instance.enumerate_stops()
    yield


test_now = datetime.datetime(2025, 4, 21, 7, 0, 0)


@pytest.fixture(autouse=True)
def mock_datetime_now():
    """Fixture to mock datetime.datetime.now() to return a fixed date and time."""
    with mock.patch('datetime.datetime', wraps=datetime.datetime) as mock_datetime:
        mock_datetime.now.return_value = test_now
        print(datetime.datetime.now())
        yield mock_datetime


@pytest.fixture(autouse=True)
def mock_fetch_vehicles_GTFSR(monkeypatch, vars):
    """Fixture to mock the fetch_vehicles method of GTFSR."""
    def fake_live_bus_date():
        return {
            "header": {
                "gtfs_realtime_version": "2.0",
                "incrementality": "FULL_DATASET",
                "timestamp": "1740487668"
            },
            "entity": [
                {
                    "id": "V1",
                    "vehicle": {
                        "trip": {
                            "trip_id": vars.trip_id,
                            "start_time": "11:30:00",
                            "start_date": "20250225",
                            "schedule_relationship": "SCHEDULED",
                            "route_id": "4434_85714",
                            "direction_id": 0
                        },
                        "position": {
                            "latitude": 53.2868805,
                            "longitude": -6.78756618
                        },
                        "timestamp": datetime.datetime(2025, 4, 21, 6, 59, 0).timestamp(),
                        "vehicle": {
                            "id": vars.bus_id
                        }
                    }
                },
            ]
        }

    monkeypatch.setattr(
        'bus_model.routes.all_routes.GTFSR.fetch_vehicles', fake_live_bus_date)
    update_realtime()
    yield


@pytest.fixture(autouse=True)
def mock_bus_info(vars):
    cleaned_slug = vars.bus_id
    bus_obj = model.Bus(
        slug=cleaned_slug)
    bus_obj.set_details(
        reg="212-C-12345",
        fleet_code="141",
        name="Mercedes-Benz Citaro O530",
        style="",
        fuel="diesel",
        double_decker=False,
        coach=True,
        electric=False,
        livery={
            "id": 1070,
            "name": "9",
            "left": "repeating-conic-gradient(from 227deg at 78% 97%,#0000 0deg 90deg,#fff 90deg 95deg,#fff0 95deg 97deg,#fff 97deg 102deg,#0000 102deg 360deg),linear-gradient(235deg,#f18602 45%,#1da6c2 45%)",
            "right": "repeating-conic-gradient(from 301deg at 22% 97%,#0000 0deg 90deg,#fff 90deg 95deg,#fff0 95deg 97deg,#fff 97deg 102deg,#0000 102deg 360deg),linear-gradient(125deg,#f18602 45%,#1da6c2 45%)"
        },
        withdrawn=False,
        special_features="",
    )
    yield bus_obj
