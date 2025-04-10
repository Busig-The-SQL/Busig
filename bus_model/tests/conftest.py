import datetime
import pytest

from bus_model.app import create_app
from bus_model.config import TestConfig
from bus_model.helpers.transit_entities import Bus, Stop, Route, Trip, BusStopVisit, Service, Agency, Shape, Point

@pytest.fixture()
def app():
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
    bus = Bus(slug=vars.bus_id)
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
    route = Route(
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
    trip = Trip(
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
    stop = Stop(
        stop_id=vars.stop_id1,
        stop_code=vars.stop_code1,
        stop_name="IDA Ovens",
        stop_lat=51.876872,
        stop_lon=-8.638645
        )
    yield stop

@pytest.fixture()
def stop2_instance(vars):
    stop = Stop(
        stop_id=vars.stop_id2,
        stop_code=vars.stop_code2,
        stop_name="Wood Road",
        stop_lat=51.880502,
        stop_lon=-8.635589
        )
    yield stop

@pytest.fixture()
def agency_instance(vars):
    agency = Agency(
        agency_id=vars.agency_id,
        agency_name="Bus Éireann"
        )
    yield agency

@pytest.fixture()
def service_instance(vars):
    service = Service(
        service_id=vars.service_id,
        monday=True,
        tuesday=False,
        wednesday=True,
        thursday=True,
        friday=False,
        saturday=True,
        sunday=True,
        start_date=datetime.date(2025, 7, 3),
        end_date=datetime.date(2025, 9, 21)
    )
    yield service

@pytest.fixture()
def bus_stop_visit1_instance(vars, trip_instance, stop1_instance, stop2_instance):
    """Fixture to create a BusStopVisit instance. Depends on Trip and Stop classes existence."""
    bus_stop_visit = BusStopVisit(
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
    bus_stop_visit = BusStopVisit(
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
    shape = Shape(
        shape_id=vars.shape_id,
    )
    yield shape

@pytest.fixture()
def shape_filled_instance(vars):
    shape = Shape(
        shape_id=vars.shape_id,
    )
    shape.add_point(51.876872, -8.638645, 0, 0)
    shape.add_point(51.880502, -8.635589, 0, 100.2)
    shape.add_point(51.882502, -8.635329, 0, 200.2)
    yield shape

@pytest.fixture(autouse=True, scope="session")
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
    shape_filled_instance
):
    """Using this fixture will ensure all test objects exist test process, instead of manually importing each.
       All but shape_unfilled
    """
    yield