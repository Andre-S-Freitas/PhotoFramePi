import json
import threading

CONFIG_FILE = 'config.json'

class Config:

    def __init__(self):
        self.lock = threading.Lock()     
        self.dict = self._load()

    def _load(self) -> dict:
        with self.lock:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
            return config
    
    def reload(self):
        self.dict = self._load()
    
    def get(self, key: str):
        return self.dict[key]
    
    def set(self, key: str, value):
        self.dict[key] = value

    def set_and_save(self, key: str, value):
        self.set(key=key, value=value)
        self.save()

    def save(self):
        with self.lock:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.dict, f, indent=4)

    def get_all(self) -> dict:
        return self.dict