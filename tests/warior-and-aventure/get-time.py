from adb_auto.screen import Screen

TimeBox = Screen.Area((650, 605), (779, 652))
GameSetting = Screen.Area((424, 553), (659, 597))

ProfilePos = (70, 152)
SaveSettingPos = (524, 1825)


def main():
    Screen.tap(ProfilePos, force_reload=True)
    print(Screen.get_text(GameSetting))
    print(Screen.get_text(TimeBox))
    Screen.tap(SaveSettingPos)


if __name__ == "__main__":
    main()
