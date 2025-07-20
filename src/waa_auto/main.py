from waa_auto.get_time import GameTime, GameEvent
from time import sleep
from adb_auto.config.setting import RELOAD_INTERVAL


def main():
    GameTime.update_time()
    while True:
        if GameEvent.demon_invasion_1st_wave():
            print("Can fight demon now")
        sleep(RELOAD_INTERVAL)


if __name__ == "__main__":
    main()
