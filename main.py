import sys

from PyQt5.QtWidgets import QApplication

from window import window


def main():
    conf = {
        "window_title": "Minesweeper Variants",
        "rule": "W",
        "iterate_forever": False,
    }
    app = QApplication(sys.argv)
    main_window = window.MyWindow(conf)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
