from dataclasses import dataclass
import io
import base64
from typing import Tuple
from PIL import Image
from pytesseract import Output, image_to_data


class Screen:
    reload = True
    reload_interval = 3

    screen_data = None
    screen_image: Image.Image

    @dataclass
    class Area:
        x: Tuple[float, float]
        y: Tuple[float, float]

    class AreaFactory:
        @staticmethod
        def area_from_percented(
            x: Tuple[float, float],
            y: Tuple[float, float],
        ):
            a = Screen.Area((0, 0), (0, 0))
            width, height = Screen.screen_image.size
            a.x = (int(x[0] * width), int(x[1] * width))
            a.y = (int(y[0] * height), int(y[1] * height))
            return a

    @staticmethod
    def update():
        if not Screen.screen_data:
            print("[INFO] failed to update Image data")
            return
        io_bytes = io.BytesIO(Screen.screen_data)
        Screen.screen_image = Image.open(io_bytes)

    @staticmethod
    def get_text(area: None | Area = None):
        if not Screen.screen_image:
            return
        image = Screen.screen_image
        if area:
            image = image.crop((area.x[0], area.y[0], area.x[1], area.y[1]))
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
