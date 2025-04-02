from helpers import transit_entities as model
from config import ProductionConfig

import datetime
import os
import requests
import subprocess
import time

from flask import Flask, g, abort, jsonify, request, has_request_context
from helpers.gtfsr import GTFSR, StaticGTFSR, BustimesAPI
from GTFS_Static.db_funcs import get_route_id_to_name_dict
from dotenv import load_dotenv
from math import ceil
from routes.all_routes import app as bp
from routes.all_routes import update_bus, update_realtime


subprocess.Popen(["service", "cron", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

load_dotenv()
training_uri = os.getenv("TRAINING_URI")

def create_app(config=ProductionConfig):
    """A Flask App Factory."""
    app = Flask(__name__)
    if config:
        app.config.from_object(config)
    return app

app = create_app()
app.register_blueprint(bp)

app.config["healthy"] = False

load_before = time.time()
StaticGTFSR.load_all_files()



update_bus()                    # Update the bus data on startup
update_realtime()               # Update the realtime data on startup
print(f"Loaded in {time.time() - load_before} seconds")
print("Loaded")

app.config["healthy"] = True