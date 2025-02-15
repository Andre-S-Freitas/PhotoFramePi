import os

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

PHOTO_DIR = os.path.join(BASE_DIR, 'static', 'photos')
THUMBNAIL_DIR = os.path.join(BASE_DIR,'static', 'thumbnails')
FONTS_DIR = os.path.join(BASE_DIR, 'static', 'fonts')

CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

PHOTO_LIST_FILE = os.path.join(BASE_DIR, 'photo-list.json')