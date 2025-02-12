import json
import threading

PHOTO_LIST_FILE = 'photo-list.json'

class PhotoList:
    def __init__(self):
        self.lock = threading.Lock()
        self.dict = self._load()
    
    def _load(self):
        with self.lock:
            with open(PHOTO_LIST_FILE) as f:
                return json.load(f)
    
    def reload(self):
        self.dict = self._load()
    
    def get(self, photo_id):
        for photo in self.dict['photos']:
            if photo['id'] == photo_id:
                return photo
        return None

    def save(self):
        with self.lock:
            with open(PHOTO_LIST_FILE, 'w') as f:
                json.dump(self.dict, f, indent=4)

    def add(self, photo):
        self.dict['photos'].append(photo)

    def set_active(self, photo_id):
        for photo in self.dict['photos']:
            photo['active'] = photo['id'] == photo_id

    def set_active_and_save(self, photo_id):
        self.set_active(photo_id)
        self.save()

    def add_and_save(self, photo):
        self.add(photo=photo)
        self.save()

    def remove(self, photo_id: str):
        self.dict['photos'] = [p for p in self.dict['photos'] if p['id'] != photo_id]

    def remove_and_save(self, photo_id: str):
        self.remove(photo_id=photo_id)
        self.save()

    def get_all(self) -> list:
        return self.dict['photos']