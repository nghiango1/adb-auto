import base64
from dataclasses import dataclass
import io
import time
import logging
from typing import Tuple
from datetime import timedelta

from PIL import Image
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
    top_padding = 80

    device = Device()

    @dataclass
    class Pos:
        x: float
        y: float
        screen_size: Tuple[float, float] = (1080, 2340)  # A50s
        top_padding: int = 80  # A50s

        def to_tuple(self):
            return (self.x, self.y)

        def to_percented(self):
            return (
                self.x / self.screen_size[0],
                (self.y - self.top_padding) / self.screen_size[1],
            )

        def __repr__(self):
            return f"Pos({self.x}, {self.y})"

    class PosFactory:
        @staticmethod
        def pos_from_percented(x: float, y: float):
            p = Screen.Pos(0, 0)
            width, height = Screen.screen_image.size
            p.x, p.y = int(x * width), int(y * height + Screen.top_padding)
            return p

    @dataclass
    class Area:
        top_left: Tuple[float, float]
        bottom_right: Tuple[float, float]
        screen_size: Tuple[float, float] = (1080, 2340)  # A50s
        top_padding: int = 80  # A50s

        def to_tuple(self):
            return (
                self.top_left[0],
                self.top_left[1],
                self.bottom_right[0],
                self.bottom_right[1],
            )

        def to_percented(self):
            return (
                self.top_left[0] / self.screen_size[0],
                (self.top_left[1] - self.top_padding) / self.screen_size[1],
                self.bottom_right[0] / self.screen_size[0],
                (self.bottom_right[1] - self.top_padding) / self.screen_size[1],
            )

        def __repr__(self):
            return f"area({self.top_left[0]}, {self.top_left[1]}, {self.bottom_right[0]}, {self.bottom_right[1]})"

    class AreaFactory:
        @staticmethod
        def area_from_percented_v2(
            x: float,
            y: float,
            u: float,
            v: float,
        ):
            a = Screen.Area((0, 0), (0, 0))
            width, height = Screen.screen_image.size
            a.top_left = (int(x * width), int(y * height + Screen.top_padding))
            a.bottom_right = (int(u * width), int(v * height + Screen.top_padding))
            return a

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
    def get_text(area: None | Area = None, return_image=False, percented=False):
        if not Screen.screen_data():
            return
        image = Screen.screen_image
        if area:
            if percented:
                print(area)
                area = Screen.AreaFactory().area_from_percented_v2(*area.to_percented())
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
    def tap(pos: Pos, force_reload=False, percented=False):
        if not Screen.screen_image:
            return
        x, y = pos.x, pos.y
        if percented:
            p = Screen.PosFactory.pos_from_percented(*Screen.Pos(x, y).to_percented())
            x, y = p.x * 100, p.y * 100
        Screen.device.inputTap(x, y, percented)
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
