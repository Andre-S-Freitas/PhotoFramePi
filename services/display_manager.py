import logging
import random
from services.config import Config
from services.directories import FONTS_DIR, PHOTO_DIR
from services.photo import resize_image
from services.photo_list import PhotoList
from PIL import Image, ImageDraw, ImageFont
import os

logger = logging.getLogger(__name__)


class DisplayManager: 
    def __init__(self, config: Config, photo_list: PhotoList):
        self.config = config
        self.photo_list = photo_list
        try:
            from inky.auto import auto # type: ignore
            self.display = auto()
            config.set_and_save("resolution", [int(self.display.resolution[0]), int(self.display.resolution[1])])
        except ImportError:
            self.display = None
        

    def choose_next_photo(self):
        self.photo_list.reload()
        photos = self.photo_list.get_all()

        match len(photos):
            case 0:
                return (None, None)
            case 1: 
                photo = photos[0]
            case _:
                photos = [photo for photo in photos if not photo['active']]
                photo = random.choice(photos)
        
        photo_path = os.path.join(PHOTO_DIR, photo['id'])
        image = Image.open(photo_path)
        return (image, photo['id'])
    
    def show_next_photo(self, photo_id):
        self.photo_list.reload()
        photos = self.photo_list.get_all()

        for photo in photos:
            if photo['id'] == photo_id:
                photo_path = os.path.join(PHOTO_DIR, photo['id'])
                return (Image.open(photo_path), photo_id)
        return (None, None)

    def show_new_image(self, image, photo_id):
        x, y = self._get_resolution()
        image = resize_image(image, (x, y))
        
        self.photo_list.set_active_and_save(photo_id)
        self._update_display(image)
             
    def show_message(self, title: str, message: str):
        w, h = self._get_resolution()
        image = Image.new("P", (w, h), color="white")
        image_draw = ImageDraw.Draw(image)
        
        title_font_path = os.path.join(FONTS_DIR, 'Jost-SemiBold.ttf')
        title_font = ImageFont.truetype(title_font_path, 30)
        title_height = DisplayManager.get_text_height(title_font, title)

        message_font_path = os.path.join(FONTS_DIR, 'Jost.ttf')
        message_font = ImageFont.truetype(message_font_path, 20)
        message_line_height = DisplayManager.get_text_height(message_font, message)

        wrapped_lines = DisplayManager.wrap_lines(message, image_draw, message_font, w)
        total_text_height = len(wrapped_lines) * message_line_height
        longest_line_width = max([image_draw.textlength(line, font=message_font) for line in wrapped_lines])

        y = max((h - total_text_height - title_height) // 2, 0)
        x = w // 2

        image_draw.text((x, y), title, fill="black", anchor='mm', font=title_font)
        y += title_height
        x -= longest_line_width // 2

        for line in wrapped_lines:
            image_draw.text((x, y), line, fill="black", anchor='lt', font=message_font)
            y += message_line_height

        self._update_display(image)

    def _update_display(self, image):
        if self.display is not None:
            self.display.set_image(image)
            self.display.show()
        else:
            logger.warning("No display detected, outputting to file: 'display.png'")
            image.save("display.png")

    @staticmethod
    def get_text_height(font: ImageFont.FreeTypeFont, text: str):        
        # Word-wrap text using pixel-based constraints
        left, top, right, bottom = font.getbbox(text)
        return bottom - top
    
    @staticmethod
    def wrap_lines(message, image_draw, font, max_text_width):        
        # Word-wrap text using pixel-based constraints
        words = message.replace("\n", " \n").split(" ")
        wrapped_lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = image_draw.textlength(test_line.replace("\n", ""), font=font)
            if test_width <= max_text_width and "\n" not in word:
                current_line.append(word)
            else:
                wrapped_lines.append(' '.join(current_line))
                current_line = [word.replace("\n", "")]

        if current_line:
            wrapped_lines.append(' '.join(current_line))
        return wrapped_lines

    def _get_resolution(self):
        if self.config.get('orientation') == 'portrait':
            return (self.config.get('resolution')[1], self.config.get('resolution')[0])
        return (self.config.get('resolution')[0], self.config.get('resolution')[1])