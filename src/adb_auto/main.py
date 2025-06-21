from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton
import sys

from adb_auto.adb.device import Device


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hello World")

        button = QPushButton("My sample app.")
        button.pressed.connect(self.close)

        self.setCentralWidget(button)
        self.show()

    def show_image(self, image):
        """Show image"""

        self.title = "Image"
        self.setWindowTile(self.title)

        label = QLabel(self)


def main():
    device = Device()
    device.take_screenshot()
    # for i in [1, 10, 100, 200, 300, 400, 500]:
    #     device.inputTap(i, i)

    app = QApplication(sys.argv)
    w = MainWindow()
    app.exec()


if __name__ == "__main__":
    main()
