from adb_auto.screen import Screen
from adb_auto.utils.redis_helper import r


screen_data = r.set("screen_data", bytes(b"sample"))
assert Screen.screen_data() == "sample"
