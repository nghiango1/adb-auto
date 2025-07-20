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
                    if len(name) > 3:
                        res["_".join([x, y])] = name

            if len(res) == 0:
                retry -= 1
                continue
            curr = res[MapMove.Entries.CURR.value]
            if curr not in MapMove.know_map:
                print(f"[WARN] Unknow placed, found {curr}")
                if DEBUG:
                    r.sadd(MapMove.REDIS_KEY_SKNOW_MAP, curr)
                    MapMove.know_map.add(curr)
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
        Screen.tap(pos)
        MapMove.update()


def main():
    import json

    MapMove.know_map = r.smembers(MapMove.REDIS_KEY_SKNOW_MAP)
    MapMove.know_map = set([i.decode("ascii") for i in MapMove.know_map])
    MapMove.update()

    know_edges = r.smembers(MapMove.REDIS_KEY_SKNOW_MAP_EDGE)
    know_edges = set([i.decode("ascii") for i in know_edges])

    nexts = set([v for k, v in MapMove.full_map.items()]) ^ set([MapMove.pos])
    edges = set([f"{MapMove.pos}|||{n}" for n in nexts])
    remain = edges ^ (edges & know_edges)
    print(
        f"[INFO] curr map = {MapMove.pos}, known_map = {know_edges}, remain = {remain}"
    )
    while len(remain) > 0:
        print(f"[INFO] found unknow map at {remain}")
        reverse = {v: k for k, v in MapMove.full_map.items()}
        flag = False
        for edge in remain:
            n = edge.split("|||")[1]
            k = reverse[n]
            print(f"[INFO] Try to follow {edge} go to {n} ({k})")
            curr = MapMove.pos
            MapMove.move(k)
            if MapMove.pos == curr:
                print(f"[WARN] Found invalid map {n} ({k})")
                r.srem(MapMove.REDIS_KEY_SKNOW_MAP, n)
                MapMove.know_map.remove(n)
            else:
                r.sadd(MapMove.REDIS_KEY_SKNOW_MAP, f"{n}")
                MapMove.know_map.add(n)
                r.sadd(MapMove.REDIS_KEY_SKNOW_MAP_EDGE, f"{curr}|||{n}")
                r.sadd(MapMove.REDIS_KEY_SKNOW_MAP_EDGE, f"{curr}|||{MapMove.pos}")
                know_edges.add(f"{curr}|||{n}")
                know_edges.add(f"{curr}|||{MapMove.pos}")
                flag = True
                break
        if not flag:
            print("[ERROR] Can't seem to find any path")
            break

        nexts = set([v for k, v in MapMove.full_map.items()]) ^ set([MapMove.pos])
        edges = set([f"{MapMove.pos}|||{n}" for n in nexts])
        remain = edges ^ (edges & know_edges)


if __name__ == "__main__":
    main()
