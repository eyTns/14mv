import pytest
from PyQt5.QtWidgets import QApplication, QMainWindow
from window.window import MyWindow
from window.utils import compare_image_same
import os
import sys

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
    # images_root path: C:\Users\james\Documents\GitHub\Minesweeper-Variants\images
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path_1 = os.path.join(root_path, "images", "cell_blank.png")
    image_path_2 = os.path.join(root_path, "images", "cell_blank_2.png")
    image_path_3 = os.path.join(root_path, "screenshot_region.png")
    assert compare_image_same(image_path_1, image_path_2)
    assert compare_image_same(image_path_1, image_path_3)
    assert compare_image_same(image_path_2, image_path_2)


