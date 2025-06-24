import base64
import os
import sys
import json
import threading
import time

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton
from flask import Flask, render_template, url_for

from adb_auto.adb.device import Device

SCREENSHOT_IMAGES = "/tmp/screen.png"
RELOAD_INTERVAL = 3
RELOAD_INTERVAL_MS = RELOAD_INTERVAL * 1000
VERBOSE = False


def debug(*arg):
    if VERBOSE:
        print(*arg)


class FlaskApp:
    app = Flask(__name__)
    screen_data = None
    reload_screen = False

    @staticmethod
    def encode_image_base64(image_path):
        if not os.path.exists(image_path):
            return "Image not found"

        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")
            ext = image_path.split(".")[-1]
            return f"data:image/{ext};base64,{encoded}"

    @staticmethod
    def encode_mem_image_base64(data):
        encoded = base64.b64encode(data).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    @app.route("/")
    def home():
        print(
            f"[INFO] First load image: `{SCREENSHOT_IMAGES}`, check_valid: {os.path.isfile(SCREENSHOT_IMAGES)}"
        )
        image_data = FlaskApp.encode_image_base64(SCREENSHOT_IMAGES)
        return render_template("index.html", image_data=image_data)

    @app.route("/current-image")
    def current_image():
        if not FlaskApp.screen_data:
            debug(
                f"[INFO] Reload image: `{SCREENSHOT_IMAGES}`, check_valid: {os.path.isfile(SCREENSHOT_IMAGES)}"
            )
            image_data = FlaskApp.encode_image_base64(SCREENSHOT_IMAGES)
        else:
            debug("[INFO] Reload in-memory image")
            image_data = FlaskApp.encode_mem_image_base64(FlaskApp.screen_data)
        return json.dumps({"image_data": image_data})

    @app.route("/togger-reload")
    def togger_reloading():
        FlaskApp.reload_screen = not FlaskApp.reload_screen
        return json.dumps({"reload_screen": FlaskApp.reload_screen})


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hello World")

        button = QPushButton("My sample app.")
        button.pressed.connect(self.close)

        self.setCentralWidget(button)
        self.show()

    def show_image(self, image):
        """Show image"""

        self.title = "Image"
        self.setWindowTile(self.title)

        label = QLabel(self)


def reload_screen_shot_image(device):
    while not FlaskApp.reload_screen:
        FlaskApp.screen_data, _path = device.take_screenshot(to_file=False)
        time.sleep(RELOAD_INTERVAL)


def main():
    device = Device()
    device.take_screenshot()
    # for i in [1, 10, 100, 200, 300, 400, 500]:
    #     device.inputTap(i, i)

    threading.Thread(target=reload_screen_shot_image, args=(device,)).start()
    FlaskApp.app.run(debug=False)


if __name__ == "__main__":
    main()
