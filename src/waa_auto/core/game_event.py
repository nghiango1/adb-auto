import logging
from datetime import time
from waa_auto.core.game_time import GameTime

logger = logging.getLogger(__name__)


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
