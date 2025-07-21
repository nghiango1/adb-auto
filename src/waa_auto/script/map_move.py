import logging
from adb_auto.screen import Screen
from datetime import datetime
from typing import Dict, List
from adb_auto.utils.logger import debug
from adb_auto.config.setting import DEBUG
from enum import Enum
from adb_auto.utils.redis_helper import r
import random

logger = logging.getLogger(__name__)


class MapMove:
    pos = ""
    full_map = {}

    REDIS_KEY_SKNOW_MAP_EDGE = "waa_auto:know_map_edge"
    REDIS_KEY_SKNOW_MAP = "waa_auto:know_map"
    know_map = set()
    know_edges = set()

    TOTAL_RETRY = 3

    table_x: Dict[str, List[int]] = {
        "left": [325, 565],
        "mid": [585, 820],
        "right": [840, 1070],
    }
    table_y: Dict[str, List[int]] = {
        "top": [1850, 1935],
        "mid": [1950, 2025],
        "bottom": [2050, 2125],
    }

    MapNameFallbackArea = Screen.Area((8, 1851), (313, 1949))

    class Entries(Enum):
        LEFT_TOP = "left_top"

        LEFT = "left_mid"

        LEFT_BOTTOM = "left_bottom"

        TOP = "mid_top"

        # This is just alias
        CURR = "mid_mid"

        BOTTOM = "mid_bottom"

        RIGHT_TOP = "right_top"

        RIGHT = "right_mid"

        RIGHT_BOTTOM = "right_bottom"

    @staticmethod
    def text_only(data) -> str:
        # Example return
        # {'text': [{'position': {'x': (8, 100), 'y': (9, 35)}, 'value': 'Game'}, {'position': {'x': (112, 225), 'y': (8, 42)}, 'value': 'Setting'}], 'image': {'x': 424, 'y': 553, 'width': 235, 'height': 44, 'data': ''}}
        debug(f"[INFO] (text_only) Found = {data}")
        texts = data.get("text", [])
        grouped_text = []
        for ins in texts:
            val = ins.get("value", "")
            if val:
                grouped_text.append(val)

        res = " ".join(grouped_text)
        debug(f"[INFO] (text_only) Grouped text = {res}")

        return res

    @staticmethod
    def get_area(entry: Entries | str):
        if isinstance(entry, str):
            x, y = tuple(entry.split("_"))
        else:
            x, y = tuple(entry.value.split("_"))
        print(x, y)
        entry_x = MapMove.table_x[x]
        entry_y = MapMove.table_y[y]

        top_left = (entry_x[0], entry_y[0])
        bottom_right = (entry_x[1], entry_y[1])
        return Screen.Area(top_left, bottom_right)

    @staticmethod
    def get_full_map() -> Dict[str, str]:
        res = {}
        retry = MapMove.TOTAL_RETRY

        while retry > 0:
            for x, entry_x in MapMove.table_x.items():
                for y, entry_y in MapMove.table_y.items():
                    top_left = (entry_x[0], entry_y[0])
                    bottom_right = (entry_x[1], entry_y[1])
                    name = MapMove.text_only(
                        Screen.get_text(Screen.Area(top_left, bottom_right))
                    )
                    if x == "mid" and y == "mid" and len(name) < 3:
                        print(
                            "[WARN] Current map can't be processed, using advance pre-processing"
                        )
                        if len(name) < 3:
                            print("[WARN] Can't get current map name, use fallback")
                            name = MapMove.text_only(
                                Screen.get_text(MapMove.MapNameFallbackArea)
                            )
                        if len(name) < 3:
                            print("[WARN] Can't get current map name, use binary_thresholding")
                            name = MapMove.text_only(
                                Screen.get_text(
                                    Screen.Area(top_left, bottom_right),
                                    binary_thresholding=True,
                                )
                            )
                        if len(name) < 3:
                            print("[WARN] Can't get current map name, use fallback with binary_thresholding")
                            name = MapMove.text_only(
                                Screen.get_text(
                                    MapMove.MapNameFallbackArea,
                                    binary_thresholding=True,
                                )
                            )
                        if len(name) < 3:
                            print("[WARN] Can't get current map name, use placeholder")
                            name = "Placeholder"

                    if len(name) > 3:
                        res["_".join([x, y])] = name

            if len(res) == 0:
                retry -= 1
                continue
            curr = res[MapMove.Entries.CURR.value]
            if curr not in MapMove.know_map:
                print(f"[WARN] Unknow placed, found {curr}")
            break

        return res

    @staticmethod
    def update():
        MapMove.full_map = MapMove.get_full_map()
        print(f"[INFO] map = {MapMove.full_map}")
        MapMove.pos = MapMove.full_map[MapMove.Entries.CURR.value]

    @staticmethod
    def random_in_between(a: Screen.Area):
        x, y, u, v = a.to_tuple()
        width = u - x
        height = v - y
        return x + width / 2, y + height / 2

    @staticmethod
    def move(next: Entries | str):
        area = MapMove.get_area(next)
        pos = MapMove.random_in_between(area)
        print(f"[INFO] move next {next}, tap pos {pos} (in between {area})")
        Screen.tap(pos, force_reload=True)
        MapMove.update()

    @staticmethod
    def reverse():
        return {v: k for k, v in MapMove.full_map.items()}

    @staticmethod
    def add_map(name):
        r.sadd(MapMove.REDIS_KEY_SKNOW_MAP, name)
        MapMove.know_map.add(name)

    @staticmethod
    def add_edges(curr, dest, direction):
        edge_str = f"{curr}|||{dest}|||{direction}"
        r.sadd(MapMove.REDIS_KEY_SKNOW_MAP_EDGE, edge_str)
        MapMove.know_edges.add(edge_str)


def main():
    MapMove.know_edges = r.smembers(MapMove.REDIS_KEY_SKNOW_MAP_EDGE)
    MapMove.know_map = r.smembers(MapMove.REDIS_KEY_SKNOW_MAP)
    MapMove.know_map = set([i.decode("utf-8") for i in MapMove.know_map])
    MapMove.know_edges = set([i.decode("utf-8") for i in MapMove.know_edges])

    Screen.update(True)
    MapMove.update()
    MapMove.add_map(MapMove.pos)
    for direction, name in MapMove.full_map.items():
        if name == MapMove.pos:
            continue
        MapMove.add_edges(MapMove.pos, name, direction)
        MapMove.add_map(name)


if __name__ == "__main__":
    main()
