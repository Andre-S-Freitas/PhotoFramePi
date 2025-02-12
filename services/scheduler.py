import logging
import traceback
from threading import Condition, Lock, Thread

from services.config import Config
from services.display_manager import DisplayManager
from services.network import get_hostname, get_ip_address

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, config: Config, display_manager: DisplayManager):
        self.config = config
        self.display_manager = display_manager
        self.thread = None
        self.lock = Lock()
        self.condition = Condition(self.lock)

        self.count = 0

    def start(self):
        if self.thread is None:
            logger.info('Starting scheduler...')
            self.thread = Thread(target=self._run, name='Scheduler' ,daemon=True)
            self.running = True
            self.thread.start()

            self.photo_id = None

    def stop(self):
        with self.condition:
            self.running = False
            self.condition.notify_all() 
        if self.thread:
            logger.info('Stopping scheduler...')
            self.thread.join()
    
    def _run(self):
        while True:
            try: 
                with self.condition:
                    self.count += 1
                    logger.info(f'Checking... {self.count}')
                    self.condition.wait(int(self.config.get('interval')))
            
                    if not self.running:
                        break

                    logger.info('Updating display...')

                    if self.photo_id:
                        image, photo_id = self.display_manager.show_next_photo(self.photo_id)
                    else:
                        image, photo_id = self.display_manager.choose_next_photo()

                    if image:
                        self.display_manager.show_new_image(image, photo_id)
                    else:
                        message = '\nTo upload photos, visit:'
                        message += f'\n        http://{get_ip_address()} or'
                        message += f'\n        http://{get_hostname()}'
                        self.display_manager.show_message('No photos found', message)

                    self.photo_id = None
            
            except Exception:
                self.display_manager.show_message('Error in Scheduler:', traceback.format_exc())
                logger.exception('Error in Scheduler:')
                break


    def update_photo(self, id):
        with self.condition:
            self.photo_id = id
            self.condition.notify_all()

    def update_config(self):
        with self.condition:
            self.condition.notify_all()

    