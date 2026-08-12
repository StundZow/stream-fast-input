import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from spotifyswitcher.main_window import MainWindow
from spotifyswitcher.resources import ICON_PATH


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(ICON_PATH))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
