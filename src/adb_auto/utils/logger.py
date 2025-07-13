import traceback
from config.setting import VERBOSE


def debug(*arg, error=False):
    if error:
        print("[ERROR]", *arg)
        print("Full traceback", traceback.print_exc())
    elif VERBOSE:
        print(*arg)
