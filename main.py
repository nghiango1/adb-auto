from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton
from adb import Device


def main():
    device = Device()
    device.take_screenshot()
    for i in [1, 10, 100, 200, 300, 400, 500]:
        device.inputTap(i, i)


if __name__ == "__main__":
    main()
