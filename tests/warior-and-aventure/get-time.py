import logging
from typing import Optional
from adb_auto.screen import Screen
from datetime import datetime, time
from time import sleep

TOTAL_RETRY = 3
logger = logging.getLogger(__name__)


class GameTime:
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
    def text_only(res) -> str:
        # Example return
        # {'text': [{'position': {'x': (8, 100), 'y': (9, 35)}, 'value': 'Game'}, {'position': {'x': (112, 225), 'y': (8, 42)}, 'value': 'Setting'}], 'image': {'x': 424, 'y': 553, 'width': 235, 'height': 44, 'data': ''}}
        texts = res.get("text", [])
        grouped_text = []
        for ins in texts:
            val = ins.get("value", "")
            if val:
                grouped_text.append(val)

        return " ".join(grouped_text)

    @staticmethod
    def setting_open() -> bool:
        res = Screen.get_text(GameTime.GameSetting)
        return GameTime.text_only(res) == "Game Setting"

    @staticmethod
    def get_time():
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
        curr_time_str = GameTime.text_only(Screen.get_text(GameTime.TimeBox))

        # Assumming we can close the setting
        print("[INFO] Close setting")
        Screen.tap(GameTime.SaveSettingPos)
        return GameTime.to_time(curr_time_str)


class GameEvent:
    curr_time = time(0, 0, 0)

    @staticmethod
    def update_time(curr_time: Optional[time] = None):
        print("[INFO] Update current game time for Event tracking")
        if curr_time is not None:
            GameEvent.curr_time = curr_time
        else:
            if GameEvent.curr_time == time(0, 0, 0):
                print("[WARN] Found default time value, try getting Game time again")
                curr_time = GameTime.get_time()

    @staticmethod
    def daily_reset():
        daily_reset = GameTime.after(GameEvent.curr_time, time(6, 00, 0))
        print(f"[INFO] daily_reset = {daily_reset}, at: {GameEvent.curr_time}")
        return daily_reset

    @staticmethod
    def demon_invasion_1st_wave():
        demon_invasion = GameTime.after(GameEvent.curr_time, time(16, 30, 0))
        print(
            f"[INFO] demon_invasion 1st wave = {demon_invasion}, at: {GameEvent.curr_time}"
        )
        return demon_invasion


def main():
    curr_time = GameTime.get_time()

    GameEvent.update_time(curr_time)
    GameEvent.daily_reset()
    GameEvent.demon_invasion_1st_wave()


if __name__ == "__main__":
    main()
