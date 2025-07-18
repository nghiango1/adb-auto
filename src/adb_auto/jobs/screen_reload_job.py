import logging
import threading
import time

from adb_auto.config.setting import RELOAD_INTERVAL, VERBOSE
from adb_auto.screen import Screen
from adb_auto.utils.redis_helper import r

logging.basicConfig(level=logging.ERROR)
if VERBOSE:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScreenReloadJob:
    """Syncing device screen for every setted RELOAD_INTERVAL"""

    killed = False

    @staticmethod
    def reload_screen_shot_image():
        logger.info("Started reload_screen_shot_image thread")
        while True and not ScreenReloadJob.killed:
            start = end = 0
            if r.get("screen_reload") != "false":
                start = time.time()
                data, _ = Screen.device.take_screenshot(to_file=False)
                end = time.time()
                if data:
                    r.set("screen_data", bytes(data))
                    h = hash(bytes(data))
                    logger.info(f"Reloaded and push to redis {h}")

            remain = RELOAD_INTERVAL - end - start
            if remain > 0:
                time.sleep(remain)

    thread = threading.Thread(target=reload_screen_shot_image)

    @staticmethod
    def start():
        r.set("screen_reload", "true")
        ScreenReloadJob.thread.start()

    @staticmethod
    def stop():
        ScreenReloadJob.killed = True
        ScreenReloadJob.thread.join(3)
        while ScreenReloadJob.thread.is_alive():
            logger.error("Retry exiting ScreenReloadJob background thread")
            ScreenReloadJob.thread.join(3)


if __name__ == "__main__":
    ScreenReloadJob.reload_screen_shot_image()
