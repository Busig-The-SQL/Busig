# Bus Model Container

> Manages the transfer and processing of TFI data, and fulfills requests from the front-end.

## Front-end API Endpoints

|Endpoint|Method|Note|
|--|--|--|
|`/v1/stops`|`GET`|Returns details about every stop|
|`/v1/stop/arrivals/<stop_id>`|`GET`|Returns the buses that will arrive at a given stop in the near future|
|`/v1/bus`|`GET`|Returns details about every live bus|
|`/v1/bus/<bus_id>`|`GET`|Returns a list of times the bus will stop at|
|`/v1/route`|`GET`|Retuns all routes and their associated bus stops|

## Internal Use API Endpoints

|Endpoint|Method|Note|
|--|--|--|
|`/v1/route_id_to_name`|`GET`|Returns a dict of route ids and their names|
|`/v1/update_realtime`|`GET`|Fetches new live data and updates the bus model. Also sends to `training` container|
|`/v1/update_static`|`GET`|Fetches the latest static files and updates the database and bus model|
|`/v1/update_bus`|`GET`|Fetches the latest bus details and updates the bus model|

## Testing Locally

To run the automated tests locally, follow the following steps:

1. Run `docker exec -it bus_model bash` once the containers are running
2. Run `export PYTHONPATH=/bus_model`
3. Run `pytest tests/ --disable-warnings --cov=.`
