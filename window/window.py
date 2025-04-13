import random
import time

from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
                             QMainWindow, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from window.utils import (analyze_number_cells, capture_window_screenshot,
                          click_cell, convert_to_numeric, find_best_fit_cells,
                          find_common_areas, find_single_cell_hints, input_spacebar, find_single_clickable_cells)





class HeaderFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("Hello")
        layout.addWidget(label)


class GridFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: lightgray;")
        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)


class ScreenshotFrame(QFrame):
    def __init__(self, window_title, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        save_path = f"{window_title}.png"
        capture_window_screenshot(window_title, save_path)
        
        label = QLabel()
        label.setPixmap(QPixmap(save_path))
        layout.addWidget(label)


class HintsFrame(QFrame):
    def __init__(self, hints_data, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
    
    def process_hints(self, all_hints):
        safe_hints = sorted(list({h['location'] for h in all_hints if h['type'] == 'safe'}))
        mine_hints = sorted(list({h['location'] for h in all_hints if h['type'] == 'mine'}))
        return safe_hints, mine_hints
    
    def add_hints_section(self, title, hints, color):
        section = QLabel(title)
        section.setStyleSheet(f"font-weight: bold; color: {color};")
        self.layout.addWidget(section)
        
        for hint in hints:
            row, col = hint
            location_str = f"{row+1}{chr(65+col)}"
            hint_label = QLabel(f"• {location_str}")
            font = hint_label.font()
            font.setPointSize(12)
            hint_label.setFont(font)
            self.layout.addWidget(hint_label)

class ControlFrame(QFrame):
    def __init__(self, recapture_callback, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        recapture_button = QPushButton("Recapture")
        recapture_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        recapture_button.clicked.connect(recapture_callback)
        layout.addWidget(recapture_button)



class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        window_title = "Minesweeper Variants"
        save_path = f"{window_title}.png"
        cell_size = 6

        self.setWindowTitle("14mv solve")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.header_frame = HeaderFrame()
        self.grid_frame = GridFrame()
        self.screenshot_frame = ScreenshotFrame(window_title)
        # self.hints_frame = HintsFrame(hints_data)
        self.control_frame = ControlFrame(self.recapture)

        main_layout.addWidget(self.header_frame)
        main_layout.addWidget(self.grid_frame)
        main_layout.addWidget(self.screenshot_frame)
        # main_layout.addWidget(self.hints_frame)
        main_layout.addWidget(self.control_frame)

        self.process_game_data()
        input_spacebar(window_title)
        self.setup_window_geometry()


    def process_game_data(self):
        window_title = "Minesweeper Variants"
        save_path = f"{window_title}.png"
        cell_size = 6
        
        best_fit_cells = find_best_fit_cells(save_path, cell_size)
        numeric_grid = convert_to_numeric(best_fit_cells)
        number_cells_info = analyze_number_cells(numeric_grid)
        
        hints_single = find_single_clickable_cells(number_cells_info)
        if hints_single:
            self.process_hints(hints_single, window_title, cell_size)
            self.recapture()
            return
        
        hints_double = find_common_areas(number_cells_info)
        if hints_double:
            self.process_hints(hints_double, window_title, cell_size)
            self.recapture()
            return
        

    def process_hints(self, hints, window_title, cell_size):
        safe_hints = sorted(list({h['location'] for h in hints if h['type'] == 'safe'}))
        mine_hints = sorted(list({h['location'] for h in hints if h['type'] == 'mine'}))
        for hint in safe_hints:
            print(f"safe: {hint}")
            click_cell(window_title, hint, cell_size, right_click=False)
        for hint in mine_hints:
            print(f"mine: {hint}")
            click_cell(window_title, hint, cell_size, right_click=True)


    def setup_window_geometry(self):
        screen = QApplication.primaryScreen().geometry()
        window_size = self.sizeHint()
        self.setFixedSize(window_size)
        self.setGeometry(
            screen.width() - window_size.width(), 
            30,
            window_size.width(), 
            window_size.height()
        )


    def recapture(self):
        self.close()
        self.__init__()
        self.show()




