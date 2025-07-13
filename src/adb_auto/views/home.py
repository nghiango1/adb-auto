import os

from flask import Blueprint, render_template

from adb_auto.config.setting import SCREENSHOT_IMAGES
from adb_auto.screen import Screen
from adb_auto.utils.embedded_image import embedded_image_base64

home_view = Blueprint("home_view", __name__)


@home_view.route("/")
def home():
    print(
        f"[INFO] First load image: `{SCREENSHOT_IMAGES}`, check_valid: {os.path.isfile(SCREENSHOT_IMAGES)}"
    )
    image_data = embedded_image_base64(SCREENSHOT_IMAGES)
    return render_template(
        "index.html",
        image_data=image_data,
        reload_interval=Screen.reload_interval,
        get_current_screen_api_path="/api/v1/screen",
    )
