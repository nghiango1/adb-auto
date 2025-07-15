import threading
import time

from adb_auto.config.setting import TOTAL_DIVIDE
from adb_auto.screen import Screen
import logging

logger = logging.getLogger(__name__)


class ScreenReloadJob:
    killed = False

    @staticmethod
    def reload_screen_shot_image():
        logger.info("Started reload_screen_shot_image thread")
        while True and not ScreenReloadJob.killed:
            if Screen.reload:
                Screen.update()

    thread = threading.Thread(target=reload_screen_shot_image)

    @staticmethod
    def start():
        Screen.update()
        ScreenReloadJob.thread.start()

    @staticmethod
    def stop():
        ScreenReloadJob.killed = True
        ScreenReloadJob.thread.join(3)
        while ScreenReloadJob.thread.is_alive():
            logger.error("Retry exiting ScreenReloadJob background thread")
            ScreenReloadJob.thread.join(3)
