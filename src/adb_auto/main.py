from dataclasses import dataclass
import os
import threading
import time

from flasgger import Swagger, swag_from
from flask import Flask, jsonify, render_template, request
from config.setting import DEBUG, SCREENSHOT_IMAGES
from utils.embedded_image import embedded_image_base64

from adb_auto.adb.device import Device
from adb_auto.screen import Screen
from adb_auto.api.v1.screen import screen_api


template = {
    "swagger": "2.0",
    "info": {
        "title": "Adb Auto API",
        "description": "API for automation Android using adb",
        "version": "0.0.1",
    },
}

app = Flask(__name__)
app.config["SWAGGER"] = {"title": "Adb Auto API", "uiversion": 3}
swagger = Swagger(app, template=template)

app.register_blueprint(screen_api)


@dataclass
class ApiInfo:
    path: str
    docs: str


class ADB_AUTO_API_INFO:
    SCREEN = ApiInfo("/api/v1/screen", "docs/v1/screen.yml")


@app.route("/")
def home():
    print(
        f"[INFO] First load image: `{SCREENSHOT_IMAGES}`, check_valid: {os.path.isfile(SCREENSHOT_IMAGES)}"
    )
    image_data = embedded_image_base64(SCREENSHOT_IMAGES)
    return render_template(
        "index.html",
        image_data=image_data,
        reload_interval=Screen.reload_interval,
        get_current_screen_api_path=ADB_AUTO_API_INFO.SCREEN.path,
    )


@app.route("/api/hello")
@swag_from("docs/hello.yml")
def hello():
    name = request.args.get("name", type=str)
    result = {"result": f"hello {name}"}
    return jsonify(result)


def reload_screen_shot_image(device: Device):
    while True:
        if Screen.reload:
            Screen.screen_data, _ = device.take_screenshot(to_file=False)
            Screen.update()
        time.sleep(Screen.reload_interval)


def main():
    device = Device()
    device.take_screenshot()
    # for i in [1, 10, 100, 200, 300, 400, 500]:
    #     device.inputTap(i, i)

    threading.Thread(target=reload_screen_shot_image, args=(device,)).start()
    app.run(debug=DEBUG)


if __name__ == "__main__":
    main()
