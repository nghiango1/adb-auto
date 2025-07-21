import base64
from dataclasses import dataclass
import io
import time
import logging
from typing import Tuple
from datetime import timedelta

from PIL import Image, ImageEnhance, ImageFilter
from pytesseract import Output, image_to_data

from adb_auto.adb.device import Device
from adb_auto.config.setting import (
    RELOAD_INTERVAL,
    SCREENSHOT_IMAGES,
    GET_TEXT_SAVE_PATH,
    DEBUG,
)
from adb_auto.utils.redis_helper import r

logger = logging.getLogger(__name__)


class Screen:
    class RedisKeys:
        RELOAD_INTERVAL = "reload_interval"
        CURRENT_SCREEN = "screen_data"
        JUST_RELOAD = "just_reload"
        RELOAD_TOGGLE = "screen_reload"

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
    def update(force_reload=False):
        """Update current screen

        Args:
            force_reload (): Incase of manually reloading the screen, set this to true so that background automate won't need to run for that interval
        """
        data, _ = Screen.device.take_screenshot(to_file=False)
        if data:
            r.set(Screen.RedisKeys.CURRENT_SCREEN, bytes(data))
            if force_reload:
                r.set(
                    Screen.RedisKeys.JUST_RELOAD,
                    "true",
                    timedelta(seconds=RELOAD_INTERVAL),
                )
            logger.info(f"Reloaded and push to redis {time.time()}")

    @staticmethod
    def screen_data():
        """This take around 3s"""
        screen_data = r.get(Screen.RedisKeys.CURRENT_SCREEN)
        if not screen_data:
            logger.warn("Failed to update image data")
        io_bytes = io.BytesIO(screen_data)
        Screen.screen_image = Image.open(io_bytes)
        return screen_data

    @staticmethod
    def get_text(area: None | Area = None, return_image=False, advance_processing=True, binary_thresholding=False):
        if not Screen.screen_data():
            return
        image = Screen.screen_image
        if area:
            image = image.crop(area.to_tuple())
        if DEBUG:
            image.save(f"{GET_TEXT_SAVE_PATH}/croped-{time.time()}.png")
        if advance_processing:
            # Convert to grayscale
            gray = image.convert("L")

            # Increase contrast
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(2.0)

            # Optional: Sharpen or filter noise
            image = enhanced.filter(ImageFilter.SHARPEN)
            if DEBUG:
                image.save(f"{GET_TEXT_SAVE_PATH}/croped-{time.time()}-after-processed.png")

            # apply binary thresholding
            threshold = 128
            image = image.point(lambda x: 0 if x < threshold else 255, '1')

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

        enc = ""
        if return_image:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="PNG")
            enc = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
        result["image"] = {
            "x": area.top_left[0] if area else 0,
            "y": area.top_left[1] if area else 0,
            "width": image.width,
            "height": image.height,
            "data": f"data:image/png;base64,{enc}" if enc else "",
        }

        return result

    @staticmethod
    def tap(position: Tuple[float, float], force_reload=False):
        if not Screen.screen_image:
            return
        x, y = position
        Screen.device.inputTap(x, y)
        if force_reload:
            Screen.update(force_reload)

    @staticmethod
    def swipe(
        position1: Tuple[float, float],
        position2: Tuple[float, float],
        time: int = 200,
        force_reload=False,
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
        if force_reload:
            Screen.update(force_reload)
