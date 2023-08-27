import pytest
from PyQt5.QtWidgets import QApplication, QMainWindow
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

