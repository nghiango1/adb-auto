import os
import base64


def embedded_image_base64(image_path: str):
    """Get image from a system path and return valid embeddable data to be used in HTML <img> tag

    Args:
        image_path: Valid image path from the system

    Returns: Format into template f"data:image/{ext};base64,{encoded}"
    """
    if not os.path.exists(image_path):
        return "Image not found"

    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
        ext = image_path.split(".")[-1]
        return f"data:image/{ext};base64,{encoded}"


def embedded_mem_image_base64(data: bytes, encode: str = "png"):
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:image/{encode};base64,{encoded}"
