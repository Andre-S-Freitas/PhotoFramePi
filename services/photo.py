import uuid
from PIL import Image

ALLOWED_FILE_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# validate the file extension
def validate_extension(name):
    if '.' not in name or name.rsplit('.', 1)[1].lower() not in ALLOWED_FILE_EXTENSIONS:
        return True
    else:
        return False

def create_thumbnail(image: Image.Image):
    # resize photo to fit 240x 180
    thumbnail_size = (240, 180)
    return resize_image(image, thumbnail_size)

# generate a unique id for the photo
def generate_id():
    return uuid.uuid4()

# extract metadata from the image
def extract_data(image: Image.Image):
    resolution = image.size

    exif = image.getexif()
    taken_on = exif.get(306)
    year, month, day = '','',''
    hour, minute, second = '','',''
    if taken_on:
        year, month, day = taken_on.split(' ')[0].split(':')
        hour, minute, second = taken_on.split(' ')[1].split(':')
    
    return {
        'resolution': {
            'x': resolution[0],
            'y': resolution[1]
        },
        'taken_date': {
            'year': year,
            'month': month,
            'day': day
        },
        'taken_time': {
            'hour': hour,
            'minute': minute,
            'second': second
        },
        'active': False
    }

# resize the image to the desired size
def resize_image(image: Image.Image, desired_size, image_settings=[]):
    img_width, img_height = image.size
    desired_width, desired_height = desired_size
    desired_width, desired_height = int(desired_width), int(desired_height)

    img_ratio = img_width / img_height
    keep_width = "keep-width" in image_settings

    x_offset, y_offset = 0,0
    new_width, new_height = img_width,img_height
    # Step 1: Determine crop dimensions
    desired_ratio = desired_width / desired_height
    if img_ratio > desired_ratio:
        # Image is wider than desired aspect ratio
        new_width = int(img_height * desired_ratio)
        if not keep_width:
            x_offset = (img_width - new_width) // 2
    else:
        # Image is taller than desired aspect ratio
        new_height = int(img_width / desired_ratio)
        if not keep_width:
            y_offset = (img_height - new_height) // 2

    # Step 2: Crop the image
    cropped_image = image.crop((x_offset, y_offset, x_offset + new_width, y_offset + new_height))

    # Step 3: Resize to the exact desired dimensions (if necessary)
    return cropped_image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)