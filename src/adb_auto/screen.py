import base64
from dataclasses import dataclass
import io
import time
import logging
from typing import Tuple

from PIL import Image
from pytesseract import Output, image_to_data

from adb_auto.adb.device import Device
from adb_auto.config.setting import RELOAD_INTERVAL, SCREENSHOT_IMAGES, GET_TEXT_SAVE_PATH, DEBUG
from adb_auto.utils.redis_helper import r

logger = logging.getLogger(__name__)


class Screen:
    reload = True
    reload_interval = RELOAD_INTERVAL

    screen_image: Image.Image = Image.open(SCREENSHOT_IMAGES)

    device = Device()

    @dataclass
    class Area:
        top_left: Tuple[float, float]
        bottom_right: Tuple[float, float]

        def to_tuple(self):
            return (
                self.top_left[0],
                self.top_left[1],
                self.bottom_right[0],
                self.bottom_right[1],
            )

    class AreaFactory:
        @staticmethod
        def area_from_percented(
            x: Tuple[float, float],
            y: Tuple[float, float],
        ):
            a = Screen.Area((0, 0), (0, 0))
            width, height = Screen.screen_image.size
            a.top_left = (int(x[0] * width), int(x[1] * width))
            a.bottom_right = (int(y[0] * height), int(y[1] * height))
            return a

    @staticmethod
    def screen_data():
        """This take around 3s"""
        screen_data = r.get("screen_data")
        if not screen_data:
            logger.warn("Failed to update image data")
        io_bytes = io.BytesIO(screen_data)
        Screen.screen_image = Image.open(io_bytes)
        return screen_data

    @staticmethod
    def get_text(area: None | Area = None):
        if not Screen.screen_data():
            return
        image = Screen.screen_image
        if area:
            image = image.crop(area.to_tuple())
        if DEBUG:
            image.save(f"{GET_TEXT_SAVE_PATH}/croped-{time.time()}.png")
        data = image_to_data(image, output_type=Output.DICT)

        # Create a result with bounding box Area and text contain map
        result = {}
        result["text"] = []
        for i in range(len(data["text"])):
            if int(data["conf"][i]) > 0:
                text = data["text"][i].strip()
                if text:
                    bbox = {
                        "x": (data["left"][i], data["left"][i] + data["width"][i]),
                        "y": (data["top"][i], data["top"][i] + data["height"][i]),
                    }
                    result["text"].append({"position": bbox, "value": text})

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        enc = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
        result["image"] = {
            "width": Screen.screen_image.width,
            "height": Screen.screen_image.height,
            "data": f"data:image/png;base64,{enc}",
        }

        return result

    @staticmethod
    def tap(position: Tuple[float, float]):
        if not Screen.screen_image:
            return
        x, y = position
        Screen.device.inputTap(x, y)

    @staticmethod
    def swipe(
        position1: Tuple[float, float],
        position2: Tuple[float, float],
        time: int = 200,
    ):
        if not Screen.screen_image:
            return
        x1, y1 = position1
        x2, y2 = position2
        Screen.device.inputSwipe(
            x1,
            y1,
            x2,
            y2,
            time=time,
            percent=False,
        )
