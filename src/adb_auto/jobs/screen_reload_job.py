import threading
import time

from adb_auto.adb.device import Device
from adb_auto.config.setting import TOTAL_DIVIDE
from adb_auto.screen import Screen
from adb_auto.utils.logger import debug


class ScreenReloadJob:
    killed = False
    device = Device()

    @staticmethod
    def reload_screen_shot_image(device: Device):
        debug("[INFO] Start ScreenReloadJob thread")
        repeat_counter = 0
        total_divide = TOTAL_DIVIDE
        while True and not ScreenReloadJob.killed:
            if Screen.reload and repeat_counter > total_divide:
                Screen.screen_data, _ = device.take_screenshot(to_file=False)
                Screen.update()
                repeat_counter = 0
            time.sleep(Screen.reload_interval / total_divide)
            repeat_counter += 1

    thread = threading.Thread(target=reload_screen_shot_image, args=(device,))

    @staticmethod
    def start(device_id=""):
        if device_id:
            debug("[INFO] ScreenReloadJob try to overide default device_id")
            ScreenReloadJob.device = Device(deviceId=device_id)
        ScreenReloadJob.thread.start()

    @staticmethod
    def stop():
        ScreenReloadJob.killed = True
        ScreenReloadJob.thread.join(3)
        while ScreenReloadJob.thread.is_alive():
            debug("Retry exiting ScreenReloadJob background thread", error=True)
            ScreenReloadJob.thread.join(3)
