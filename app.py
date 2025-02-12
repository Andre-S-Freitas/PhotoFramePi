import os
from flask import Flask
from services.config import Config
from blueprints.photo import photo_route
from blueprints.main import main_route
from blueprints.config import config_route
from services.display_manager import DisplayManager
from services.photo_list import PhotoList
from services.scheduler import Scheduler

# Load config
config = Config()
photoList = PhotoList()

# Initialize Display Manager
display_manager = DisplayManager(config, photoList)

# Start the Scheduler
scheduler = Scheduler(config, display_manager)

# Create the Web Server
app = Flask(__name__)

# Register the Blueprints
app.register_blueprint(main_route)
app.register_blueprint(photo_route)
app.register_blueprint(config_route)

# Set the global variables
app.config['CONFIG'] = config
app.config['PHOTOS'] = photoList
app.config['SCHEDULER'] = scheduler
app.config['DISPLAY_MANAGER'] = display_manager

# Set the Secret Key
app.secret_key = os.urandom(24)

if __name__ == '__main__':
    try:
        # Start the Scheduler
        from werkzeug.serving import is_running_from_reloader

        if not os.environ.get('FLASK_DEBUG') or is_running_from_reloader():
            scheduler.start()

        # Start the Web Server
        app.run(host='0.0.0.0', port=80)
    finally:
        # Stop the Scheduler
        scheduler.stop()