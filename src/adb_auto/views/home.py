from flask import Blueprint, render_template

from adb_auto.config.setting import SCREENSHOT_IMAGES
from adb_auto.screen import Screen
from adb_auto.utils.embedded_image import (
    embedded_image_base64,
    embedded_mem_image_base64,
)

home_view = Blueprint("home_view", __name__)


def _get_current_screen():
    if not Screen.screen_data():
        return embedded_image_base64(SCREENSHOT_IMAGES)
    else:
        return embedded_mem_image_base64(Screen.screen_data())


@home_view.route("/")
def home():
    return render_template(
        "index.html",
        image_data=_get_current_screen(),
        reload_interval=Screen.reload_interval,
        get_current_screen_api_path="/api/v1/screen",
    )
