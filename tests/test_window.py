import pytest
from PyQt5.QtWidgets import QApplication, QMainWindow
from window.window import MyWindow
from window import utils
import os
import sys

@pytest.fixture
def app():
    app = QApplication([])
    yield app
    app.quit()
