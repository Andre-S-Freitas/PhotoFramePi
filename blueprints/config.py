
from flask import Blueprint, current_app, jsonify, request
from services.config import Config
from services.scheduler import Scheduler

config_route = Blueprint('config', __name__)

@config_route.route('/config', methods=['POST'])
def main_page():
    config: Config = current_app.config['CONFIG']
    scheduler: Scheduler = current_app.config['SCHEDULER'] 
    body = request.get_json()

    interval = body.get('interval')
    orientation = body.get('orientation')

    config.set('interval', int(interval))
    config.set('orientation', orientation)
    config.save()

    scheduler.update_config()
    
    return jsonify({"success": True, "message": "Config saved successfully"}), 200