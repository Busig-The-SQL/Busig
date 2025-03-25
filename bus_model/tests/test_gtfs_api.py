from helpers.gtfsr import GTFSR, StaticGTFSR, BustimesAPI

def test_bustimes_fetch_vehicles():
    vehicles = BustimesAPI.fetch_vehicles()
    assert vehicles is not None, "No API response"
    assert len(vehicles) > 1000, "No vehicles found"
    assert type(vehicles[0]) == dict, "Vehicle data is not a dict"

def test_GTFSR_fetch_vehicles():
    vehicles = GTFSR.fetch_vehicles()
    assert vehicles is not None, "No API response"
    if vehicles.get("entity", None) is None:
        if "statusCode" in vehicles:
            assert 1 == 0, "API error: " + vehicles.__str__()
    assert len(vehicles["entity"]) > 0, "No vehicles found"
    assert type(vehicles["entity"][0]) == dict, "Vehicle data is not a dict"

def test_GTFSR_fetch_trip_updates():
    trip_updates = GTFSR.fetch_trip_updates()
    assert trip_updates is not None, "No API response"
    assert len(trip_updates) > 0, "No trip updates found"

def test_GTFSR_fetch_gtfsr():
    gtfsr = GTFSR.fetch_gtfsr()
    assert gtfsr is not None, "No API response"
    assert len(gtfsr) > 0, "No GTFSR data found"
