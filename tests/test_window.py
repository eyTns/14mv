import os

import pytest
from PyQt5.QtWidgets import QApplication

from window import image_utils


@pytest.fixture
def app():
    app = QApplication([])
    yield app
    app.quit()


def test_image_same():
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path_1 = os.path.join(root_path, "images", "cell_blank.png")
    image_path_2 = os.path.join(root_path, "images", "cell_blank_2.png")

    print(image_utils.MSE_of_images(image_path_1, image_path_2))
    assert image_utils.compare_image_same(image_path_1, image_path_2)
