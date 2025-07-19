from waa_auto.get_time import GameTime, GameEvent
from time import sleep
import threading


def main():
    GameTime.update_time()
    while True:
        if GameEvent.demon_invasion_1st_wave():
            print("Can fight demon now")
        sleep(1)


if __name__ == "__main__":
    main()
