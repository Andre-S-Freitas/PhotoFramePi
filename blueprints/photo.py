from flask import Blueprint, current_app, jsonify, request
import os
from services.directories import PHOTO_DIR, THUMBNAIL_DIR
from services.photo import create_thumbnail, extract_data, generate_id, validate_extension
from PIL import Image, ImageOps

from services.photo_list import PhotoList
from services.scheduler import Scheduler

photo_route = Blueprint('photo', __name__)

@photo_route.route('/list', methods=['GET'])
def list_photos():
    photo_list: PhotoList = current_app.config['PHOTOS']
    return jsonify(photo_list.get_all()), 200

@photo_route.route('/set', methods=['POST'])
def set_photo():
    photo_list: PhotoList = current_app.config['PHOTOS']

    # get photo id
    photo_id = request.get_json().get('id')

    # check if photo exists
    if not photo_list.get(photo_id):
        return jsonify({"success": False, "message": "Photo not found"}), 404

    # set photo as display
    scheduler: Scheduler = current_app.config['SCHEDULER']
    scheduler.update_photo(photo_id)

    return jsonify({"success": True, "message": "Display updated"}), 200

@photo_route.route('/remove', methods=['POST'])
def remove_photo():
    photo_list: PhotoList = current_app.config['PHOTOS']

    # get photo id
    photo_id = request.get_json().get('id')

    # check if photo exists
    if not photo_list.get(photo_id):
        return jsonify({"success": False, "message": "Photo not found"}), 404

    # delete photo from list of photos
    photo_list.remove_and_save(photo_id)

    photo_path = os.path.join(PHOTO_DIR, photo_id)
    thumbnail_path = os.path.join(THUMBNAIL_DIR, photo_id)

    # delete photo and thumbnail
    try: 
        os.remove(photo_path)
        os.remove(thumbnail_path)
    except FileNotFoundError:
        pass

    return jsonify({"success": True, "message": "Display updated"}), 200

@photo_route.route('/upload', methods=['POST'])
def upload_photo():
    photo_list = current_app.config['PHOTOS']

    for key, file in request.files.items():

        # check if file is selected
        if file.filename == None or file.filename == '':
            return jsonify({"success": False, "message": "No file selected"})

        # validate file extension
        if validate_extension(file.filename):
            return jsonify({"success": False, "message": "Invalid file extension"}), 400
    
        # create id
        extension = file.filename.rsplit('.', 1)[1].lower()
        photo_id = generate_id().hex + '.' + extension
        
        # save photo
        image = Image.open(file.stream)
        image = ImageOps.exif_transpose(image)
        if image is None:
            return jsonify({"success": False, "message": "Invalid image file"}), 400
        
        file_path = os.path.join(PHOTO_DIR, photo_id)
        os.makedirs(PHOTO_DIR, exist_ok=True)
        image.save(file_path)
        
        # save thumbnail
        thumbnail = create_thumbnail(image)
        thumbnail_path = os.path.join(THUMBNAIL_DIR, photo_id)
        os.makedirs(THUMBNAIL_DIR, exist_ok=True)
        thumbnail.save(thumbnail_path)

        # extract metadata
        photo_data = extract_data(image)
        photo_data['id'] = photo_id

        # update photo list
        photo_list.add_and_save(photo_data)


    return jsonify({"success": True, "message": "Image uploaded successfully"}), 200

