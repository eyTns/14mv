import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
from window import window
from window.utils import capture_window_screenshot, find_all_templates_in_screenshot

import random

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = window.MyWindow()
    main_window.show()
    sys.exit(app.exec_())
