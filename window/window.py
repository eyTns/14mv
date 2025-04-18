from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
                             QMainWindow, QPushButton, QVBoxLayout, QWidget)

from window.image_utils import (
                                capture_window_screenshot, 
                                 convert_to_numeric,
                                find_best_fit_cells, completed_check,
                                 )
from window.utils import (analyze_number_cells, 
                          click_hints, 
                           find_common_areas,
                          find_single_clickable_cells, next_level)


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
        self.setLayout(layout)
        
        label = QLabel()
        label.setPixmap(QPixmap(f"{window_title}.png"))
        layout.addWidget(label)


class ControlFrame(QFrame):
    def __init__(self, recapture_callback, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        recapture_button = QPushButton("Recapture")
        recapture_button.setStyleSheet(
            """
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
        """
        )
        recapture_button.clicked.connect(recapture_callback)
        layout.addWidget(recapture_button)


class MyWindow(QMainWindow):
    def __init__(self, conf:dict[str, str]):
        super().__init__()

        self.conf = conf
        self.window_title = conf["window_title"]
        self.rule = conf["rule"].upper()
        self.cell_size = conf["cell_size"]

        self.process_game_data()

        self.setWindowTitle("14mv solve")
        self.setup_ui()
        self.setup_window_geometry()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.header_frame = HeaderFrame()
        self.grid_frame = GridFrame()
        self.screenshot_frame = ScreenshotFrame(self.window_title)
        self.control_frame = ControlFrame(self.start_new_process)  # 새로운 프로세스 시작 기능 연결

        main_layout.addWidget(self.header_frame)
        main_layout.addWidget(self.grid_frame)
        main_layout.addWidget(self.screenshot_frame)
        main_layout.addWidget(self.control_frame)

    def process_game_data(self):
        save_path = f"{self.window_title}.png"
        
        while True:
            capture_window_screenshot(self.window_title)
            
            if completed_check(save_path):
                next_level(self.window_title)
                continue
                
            best_fit_cells = find_best_fit_cells(save_path, self.cell_size)
            numeric_grid = convert_to_numeric(best_fit_cells)
            number_cells_info = analyze_number_cells(numeric_grid, self.rule)

            hints_single = find_single_clickable_cells(number_cells_info)
            hints_double = sorted(list(set(find_common_areas(number_cells_info))))
            
            if hints_single:
                click_hints(self.window_title, hints_single, self.cell_size)
                continue
            elif hints_double:
                click_hints(self.window_title, hints_double, self.cell_size)
                continue

            break

    def start_new_process(self):
        self.process_game_data()

        if hasattr(self, 'screenshot_frame'):
            for i in reversed(range(self.screenshot_frame.layout().count())): 
                self.screenshot_frame.layout().itemAt(i).widget().setParent(None)
            
            label = QLabel()
            label.setPixmap(QPixmap(f"{self.window_title}.png"))
            self.screenshot_frame.layout().addWidget(label)

    def setup_window_geometry(self):
        screen = QApplication.primaryScreen().geometry()
        window_size = self.sizeHint()
        self.setFixedSize(window_size)
        self.setGeometry(
            screen.width() - window_size.width(),
            30,
            window_size.width(),
            window_size.height(),
        )

    def recapture(self):
        self.close()
        self.__init__(self.conf)
        self.show()
