import json
import os

from flasgger import swag_from
from flask import Blueprint, jsonify, request

from adb_auto.config.setting import SCREENSHOT_IMAGES
from adb_auto.screen import Screen
from adb_auto.utils.embedded_image import (
    embedded_image_base64,
    embedded_mem_image_base64,
)
from adb_auto.utils.logger import debug

screen_api = Blueprint("screen_api", __name__)


@screen_api.route("/api/v1/screen/togger-reload")
@swag_from("toggle-reload.yml")
def togger_reloading():
    Screen.reload = not Screen.reload
    return json.dumps({"reload_screen": Screen.reload})


@screen_api.post("/api/v1/screen/set-interval")
@swag_from("set-interval.yml")
def set_interval():
    try:
        input = json.loads(request.data)
        assert "reload_interval" in input
        assert input["reload_interval"] > 0.3, "interval should not less than 0.3"
    except Exception as e:
        debug(f"Got error {e}", error=True)
        return json.dumps({"result": "bad request!"}), 400
    Screen.reload_interval = input["reload_interval"]
    return json.dumps({"reload_interval": Screen.reload_interval})


@screen_api.get("/api/v1/screen/get-text")
@swag_from("get-text.yml")
def get_text():
    x = request.args.get("x", type=float, default=0)
    y = request.args.get("y", type=float, default=0)
    width = request.args.get("width", type=float, default=Screen.screen_image.width)
    height = request.args.get("height", type=float, default=Screen.screen_image.height)
    area = Screen.Area((x, x + width), (y, y + height))
    return jsonify(Screen.get_text(area))


@screen_api.get("/api/v1/screen/get-text-percented")
@swag_from("get-text-percented.yml")
def get_text_percented():
    x1 = request.args.get("x1", type=float, default=0)
    y1 = request.args.get("y1", type=float, default=0)
    x2 = request.args.get("x2", type=float, default=1)
    y2 = request.args.get("y2", type=float, default=1)
    area = Screen.AreaFactory.area_from_percented((x1, x2), (y1, y2))
    return jsonify(Screen.get_text(area))


@screen_api.get("/api/v1/screen/get-text-area")
@swag_from("get-text-area.yml")
def get_text_area():
    x1 = request.args.get("x1", type=float, default=0)
    y1 = request.args.get("y1", type=float, default=0)
    x2 = request.args.get("x2", type=float, default=Screen.screen_image.width)
    y2 = request.args.get("y2", type=float, default=Screen.screen_image.height)
    area = Screen.Area((x1, x2), (y1, y2))
    return jsonify(Screen.get_text(area))


def _get_current_screen():
    if not Screen.screen_data:
        debug(
            f"[INFO] Reload image: `{SCREENSHOT_IMAGES}`, check_valid: {os.path.isfile(SCREENSHOT_IMAGES)}"
        )
        return embedded_image_base64(SCREENSHOT_IMAGES)
    else:
        debug("[INFO] Reload in-memory image")
        return embedded_mem_image_base64(Screen.screen_data)


@screen_api.get("/api/v1/screen")
@swag_from("screen.yml")
def current_image():
    return json.dumps({"image_data": _get_current_screen()})


@screen_api.get("/api/v1/screen/tap")
@swag_from("tap.yml")
def tap():
    x = request.args.get("x", type=float, default=Screen.screen_image.width)
    y = request.args.get("y", type=float, default=Screen.screen_image.height)
    Screen.tap((x, y))
    return jsonify({"res": "success"})


@screen_api.get("/api/v1/screen/swipe")
@swag_from("swipe.yml")
def swipe():
    x1 = request.args.get("x1", type=float, default=0)
    y1 = request.args.get("y1", type=float, default=0)
    x2 = request.args.get("x2", type=float, default=Screen.screen_image.width)
    y2 = request.args.get("y2", type=float, default=Screen.screen_image.height)
    Screen.swipe((x1, y1), (x2, y2))
    return jsonify({"res": "success"})
