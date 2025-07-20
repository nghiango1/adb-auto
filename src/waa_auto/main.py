from waa_auto.get_time import GameTime, GameEvent
from time import sleep
import threading
from adb_auto.screen import Screen


def main():
    Screen.top_padding = 33
    GameTime.update_time()
    # while True:
    #     if GameEvent.demon_invasion_1st_wave():
    #         print("Can fight demon now")
    #     sleep(1)


if __name__ == "__main__":
    main()
