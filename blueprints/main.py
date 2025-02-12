from flask import Blueprint, current_app, render_template
import os
from services.photo_list import PhotoList
from services.config import Config

main_route = Blueprint('main', __name__)

@main_route.route('/')
def main_page():
    photo_list: PhotoList= current_app.config['PHOTOS']
    config: Config = current_app.config['CONFIG']

    if os.environ.get('FLASK_ENV') == 'development':
        config.reload()
        photo_list.reload()
    
    return render_template('index.html', config=config.get_all(), photos=photo_list.get_all())
    
@main_route.route('/photo-list')
def photo_list():
    photo_list: PhotoList = current_app.config['PHOTOS']
    return render_template('partial/photo-list.html', photos=photo_list.get_all())
