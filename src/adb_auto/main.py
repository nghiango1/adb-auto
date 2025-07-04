import base64
from dataclasses import dataclass
import json
import os
import threading
import time
import traceback

from flasgger import Swagger, swag_from
from flask import Flask, jsonify, render_template, request

from adb_auto.adb.device import Device
from screen import Screen


SCREENSHOT_IMAGES = "/tmp/screen.png"
VERBOSE = False
DEBUG = False


def debug(*arg, error=False):
    if error:
        print("[ERROR]", *arg)
        print("Full traceback", traceback.print_exc())
    elif VERBOSE:
        print(*arg)


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


@dataclass
class ApiInfo:
    path: str
    docs: str


class ADB_AUTO_API_INFO:
    SCREEN = ApiInfo("/api/v1/screen", "docs/v1/screen.yml")


class FlaskApp:
    reload_screen = False
    reload_interval = 3  # second

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
    return render_template(
        "index.html",
        image_data=image_data,
        reload_interval=FlaskApp.reload_interval,
        get_current_screen_api_path=ADB_AUTO_API_INFO.SCREEN.path,
    )


@app.route(ADB_AUTO_API_INFO.SCREEN.path)
@swag_from(ADB_AUTO_API_INFO.SCREEN.docs)
def current_image():
    if not Screen.screen_data:
        debug(
            f"[INFO] Reload image: `{SCREENSHOT_IMAGES}`, check_valid: {os.path.isfile(SCREENSHOT_IMAGES)}"
        )
        image_data = FlaskApp.encode_image_base64(SCREENSHOT_IMAGES)
    else:
        debug("[INFO] Reload in-memory image")
        image_data = FlaskApp.encode_mem_image_base64(Screen.screen_data)
    return json.dumps({"image_data": image_data})


@app.route("/api/hello")
@swag_from("docs/hello.yml")
def hello():
    name = request.args.get("name", type=str)
    result = {"result": f"hello {name}"}
    return jsonify(result)


@app.route("/api/v1/screen/togger-reload")
@swag_from("docs/v1/screen/toggle-reload.yml")
def togger_reloading():
    FlaskApp.reload_screen = not FlaskApp.reload_screen
    return json.dumps({"reload_screen": FlaskApp.reload_screen})


@app.post("/api/v1/screen/set-interval")
@swag_from("docs/v1/screen/set-interval.yml")
def set_interval():
    try:
        input = json.loads(request.data)
        assert "reload_interval" in input
        assert input["reload_interval"] > 0.3, "interval should not less than 0.3"
    except Exception as e:
        debug(f"Got error {e}", error=True)
        return json.dumps({"result": "bad request!"}), 400
    FlaskApp.reload_interval = input["reload_interval"]
    return json.dumps({"reload_interval": FlaskApp.reload_interval})


@app.get("/api/v1/screen/get-text")
@swag_from("docs/v1/screen/get-text.yml")
def get_text():
    x = request.args.get("x", type=float, default=0)
    y = request.args.get("y", type=float, default=0)
    width = request.args.get("width", type=float, default=Screen.screen_image.width)
    height = request.args.get("height", type=float, default=Screen.screen_image.height)
    area = Screen.Area((x, x + width), (y, y + height))
    return jsonify(Screen.get_text(area))


@app.get("/api/v1/screen/get-text-percented")
@swag_from("docs/v1/screen/get-text-percented.yml")
def get_text_percented():
    x1 = request.args.get("x1", type=float, default=0)
    y1 = request.args.get("y1", type=float, default=0)
    x2 = request.args.get("x2", type=float, default=1)
    y2 = request.args.get("y2", type=float, default=1)
    area = Screen.AreaFactory.area_from_percented((x1, x2), (y1, y2))
    return jsonify(Screen.get_text(area))


@app.get("/api/v1/screen/get-text-area")
@swag_from("docs/v1/screen/get-text-area.yml")
def get_text_area():
    x1 = request.args.get("x1", type=float, default=0)
    y1 = request.args.get("y1", type=float, default=0)
    x2 = request.args.get("x2", type=float, default=Screen.screen_image.width)
    y2 = request.args.get("y2", type=float, default=Screen.screen_image.height)
    area = Screen.Area((x1, x2), (y1, y2))
    return jsonify(Screen.get_text(area))


def reload_screen_shot_image(device: Device):
    while not FlaskApp.reload_screen:
        Screen.screen_data, _ = device.take_screenshot(to_file=False)
        Screen.update()
        time.sleep(FlaskApp.reload_interval)


def main():
    device = Device()
    device.take_screenshot()
    # for i in [1, 10, 100, 200, 300, 400, 500]:
    #     device.inputTap(i, i)

    threading.Thread(target=reload_screen_shot_image, args=(device,)).start()
    app.run(debug=DEBUG)


if __name__ == "__main__":
    main()
