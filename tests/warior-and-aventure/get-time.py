from adb_auto.adb.device import Device
from adb_auto.screen import Screen
import time

TimeBox = Screen.Area((650, 605), (779, 652))
GameSetting = Screen.Area((424, 553), (659, 597))

def main():
    device = Device()

    device.inputTap(70, 152)
    time.sleep(3)
    print(Screen.get_text(GameSetting))
    time.sleep(3)
    print(Screen.get_text(TimeBox))
    time.sleep(3)
    device.inputTap(524, 1825)
    time.sleep(3)


if __name__ == "__main__":
    main()
