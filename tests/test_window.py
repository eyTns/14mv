import os
import sys

import cv2
import numpy as np
import pytest
from PyQt5.QtWidgets import QApplication, QMainWindow

from window import utils
from window.window import MyWindow


@pytest.fixture
def app():
    app = QApplication([])
    yield app
    app.quit()


def test_window_appears(app):
    window = MyWindow()
    # qtbot.addWidget(window)  # Required for interacting with the window
    window.show()
    assert isinstance(window, QMainWindow)


def test_image_same():
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path_1 = os.path.join(root_path, "images", "cell_blank.png")
    image_path_2 = os.path.join(root_path, "images", "cell_blank_2.png")

    print(utils.MSE_of_images(image_path_1, image_path_2))
    assert utils.compare_image_same(image_path_1, image_path_2)
