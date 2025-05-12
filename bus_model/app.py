from config import ProductionConfig, TestConfig
from flask import Flask
from routes.all_routes import app as bp

import os


def create_app(config=None):
    """A Flask App Factory."""
    if config is None:
        if os.environ.get("TESTING", "NO") == "YES":
            config = TestConfig
        else:
            config = ProductionConfig
    
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(bp)

    # print("Config:", config)
    # print(f"APP_FACTORY_ONLY: {app.config['APP_FACTORY_ONLY']}\nTESTING: {app.config['TESTING']}\nDEBUG: {app.config['DEBUG']}\nMAKE_DB: {app.config['MAKE_DB']}")
    
    if app.config["APP_FACTORY_ONLY"]:
        return app
    
    # Imports
    from helpers.gtfsr import StaticGTFSR
    from dotenv import load_dotenv
    from routes.all_routes import update_bus, update_realtime

    import subprocess
    import time

    # Pre Flask app setup
    subprocess.Popen(["service", "cron", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    load_dotenv()
    
    # Post Flask app setup

    app.config["healthy"] = False
    load_before = time.time()
    StaticGTFSR.load_all_files()
    update_bus()                    # Update the bus data on startup
    update_realtime()               # Update the realtime data on startup
    print(f"Loaded in {time.time() - load_before} seconds")
    print("Loaded")

    app.config["healthy"] = True
    return app

app = create_app()