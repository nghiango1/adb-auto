from waa_auto.core.game_time import GameTime
from waa_auto.core.game_event import GameEvent


def main():
    GameTime.update_time()
    GameEvent.daily_reset()
    GameEvent.demon_invasion_1st_wave()


if __name__ == "__main__":
    main()
