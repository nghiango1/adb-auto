import logging
from typing import Optional
from adb_auto.screen import Screen
from datetime import datetime, time, timedelta
from time import sleep

TOTAL_RETRY = 3
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameTime:
    curr = time(0, 0, 0)
    last_update = datetime.now()

    @staticmethod
    def to_time(curr_str: str) -> time:
        t = datetime.strptime(curr_str, "%H:%M:%S").time()
        return t

    @staticmethod
    def within(curr: time, start: time, end: time):
        return start <= curr <= end

    @staticmethod
    def after(curr: time, start: time):
        return curr >= start

    TimeBox = Screen.Area((650, 605), (779, 652))
    GameSetting = Screen.Area((424, 553), (659, 597))

    ProfilePos = (70, 152)
    SaveSettingPos = (524, 1825)

    @staticmethod
    def text_only(data) -> str:
        # Example return
        # {'text': [{'position': {'x': (8, 100), 'y': (9, 35)}, 'value': 'Game'}, {'position': {'x': (112, 225), 'y': (8, 42)}, 'value': 'Setting'}], 'image': {'x': 424, 'y': 553, 'width': 235, 'height': 44, 'data': ''}}
        print(f"[INFO] (text_only) Found = {data}")
        texts = data.get("text", [])
        grouped_text = []
        for ins in texts:
            val = ins.get("value", "")
            if val:
                grouped_text.append(val)

        res = " ".join(grouped_text)
        print(f"[INFO] (text_only) Grouped text = {res}")
        return res

    @staticmethod
    def setting_open() -> bool:
        res = Screen.get_text(GameTime.GameSetting)
        return GameTime.text_only(res) == "Game Setting"

    @staticmethod
    def get_time() -> time:
        print("[INFO] Try to get game's time")
        retry = TOTAL_RETRY
        print("[INFO] Open setting")
        while not GameTime.setting_open():
            if retry < TOTAL_RETRY:
                print("[WARN] Open setting failed, retrying")
                sleep(1)
            retry -= 1
            if retry == 0:
                print("[ERROR] Open setting failed, quit")
                logger.error("Can't open setting")
                exit(1)
            Screen.tap(GameTime.ProfilePos, force_reload=True)

        print("[INFO] Get game's time")
        res = time(0, 0, 0)
        retry = TOTAL_RETRY
        while retry > 0:
            try:
                curr_time_str = GameTime.text_only(Screen.get_text(GameTime.TimeBox))
                res = GameTime.to_time(curr_time_str)
                break
            except Exception as _:
                print("[WARN] Error getting timer, trying")
                retry -= 1

        # Assumming we can close the setting
        print("[INFO] Close setting")
        while GameTime.setting_open():
            Screen.tap(GameTime.SaveSettingPos, force_reload=True)
            print("[WARN] Error closing setting, retrying")
        return res

    @staticmethod
    def update_time(curr_time: Optional[time] = None):
        print("[INFO] Update current game time for Event tracking")
        if curr_time is not None:
            GameTime.curr = curr_time
        else:
            if GameTime.curr == time(0, 0, 0):
                print("[WARN] Found default time value, try getting Game time again")
                GameTime.curr = GameTime.get_time()
        last_update = datetime.now()

    @staticmethod
    def guess_time() -> time:
        """Guess the current game time base on the total time have passed"""
        if GameTime.curr == time(0, 0, 0):
            print("[WARN] Found default time value, try getting Game time again")
            GameTime.update_time()

        delta = datetime.now() - GameTime.last_update
        dummy_date = datetime.combine(datetime.today(), GameTime.curr)

        new_date = dummy_date + delta

        UTC_time = datetime.now()
        if new_date - UTC_time > timedelta(minutes=1):
            return UTC_time.time()
        return new_date.time()


class GameEvent:
    @staticmethod
    def daily_reset():
        daily_reset = GameTime.after(GameTime.guess_time(), time(6, 00, 0))
        print(f"[INFO] daily_reset = {daily_reset}, at: {GameTime.guess_time()}")
        return daily_reset

    @staticmethod
    def demon_invasion_1st_wave():
        demon_invasion = GameTime.after(GameTime.guess_time(), time(16, 30, 0))
        print(
            f"[INFO] demon_invasion 1st wave = {demon_invasion}, at: {GameTime.guess_time()}"
        )
        return demon_invasion


def main():
    GameTime.update_time()
    GameEvent.daily_reset()
    GameEvent.demon_invasion_1st_wave()


if __name__ == "__main__":
    main()
