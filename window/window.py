import random

from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QFrame, QGridLayout, QLabel, QMainWindow,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget, QPushButton, QApplication)

from window.utils import (
    capture_window_screenshot, 
    find_best_fit_cells, 
    convert_to_numeric, 
    analyze_number_cells, 
    find_common_areas,
    find_single_cell_hints,
)


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("14mv hint")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # First Frame
        frame1 = QLabel("Hello")
        main_layout.addWidget(frame1)

        # Second Frame
        frame2 = QFrame()
        frame2.setStyleSheet("background-color: lightgray;")
        main_layout.addWidget(frame2)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        frame2.setLayout(grid_layout)

        # 랜덤한 숫자를 표시
        # for row in range(8):
        #     for col in range(8):
        #         # image_path = f"images/cell_{(row*8 + col)%9+1}.png"
        #         image_path = f"images/cell_{random.randint(1, 9)}.png"
        #         pixmap = QPixmap(image_path)
        #         label = QLabel()
        #         label.setPixmap(pixmap)
        #         grid_layout.addWidget(label, row, col)

        # Third Frame
        window_title = "Minesweeper Variants"
        save_path = f"{window_title}.png"
        capture_window_screenshot(window_title, save_path)
        if capture_window_screenshot(window_title, save_path):
            print(f"Screenshot saved as {save_path}")
        else:
            print("Failed to capture screenshot")

        frame3 = QLabel()
        frame3.setPixmap(QPixmap(save_path))
        main_layout.addWidget(frame3)

        # # Fourth Frame
        # screenshot_path = save_path
        # template_path = "images/cell_blank.png"
        # positions = find_all_templates_in_screenshot(screenshot_path, template_path)

        # if positions:
        #     print(f"Found {len(positions)} occurrences of the template image at positions:")
        #     for position in positions:
        #         print(position)
        # else:
        #     print(f"Template {template_path} not found in the screenshot.")

        # Fourth Frame
        screenshot_path = save_path
        cell_size = 6
        best_fit_cells = find_best_fit_cells(screenshot_path, cell_size)
        print(best_fit_cells)

        # frame4 = QFrame()
        # layout = QVBoxLayout()
        # # Create a QTableWidget with 6 rows and 6 columns
        # table = QTableWidget(6, 6)
        # for i, row in enumerate(best_fit_cells):
        #     for j, cell in enumerate(row):
        #         item = QTableWidgetItem(cell)
        #         table.setItem(i, j, item)
        # layout.addWidget(table)
        # frame4.setLayout(layout)
        # main_layout.addWidget(frame4)



        # # Fifth Frame
        # for i in range(1, 9+1):
        #     screenshot_path = save_path
        #     template_path = f"images/cell_{i}.png"
        #     positions = find_all_templates_in_screenshot(screenshot_path, template_path)

        #     if positions:
        #         print(f"Found {len(positions)} occurrences of the template cell {i} at positions:")
        #         for position in positions:
        #             print(position)
        #     else:
        #         print(f"Template {template_path} not found in the screenshot.")


        # Fifth Frame
        numeric_grid = convert_to_numeric(best_fit_cells)
        print(numeric_grid)
        number_cells_info = analyze_number_cells(numeric_grid)
        print(number_cells_info)
        hints_single = find_single_cell_hints(number_cells_info)
        print(hints_single)
        hints_double = find_common_areas(number_cells_info)
        print(hints_double)

        all_hints = hints_single + hints_double

        frame5 = QFrame()
        layout5 = QVBoxLayout(frame5)

        safe_hints = sorted(list({h['location'] for h in all_hints if h['type'] == 'safe'}))
        mine_hints = sorted(list({h['location'] for h in all_hints if h['type'] == 'mine'}))
        
        safe_section = QLabel("안전한 셀:")
        safe_section.setStyleSheet("font-weight: bold; color: green;")
        layout5.addWidget(safe_section)
        for hint in safe_hints:
            row, col = hint
            location_str = f"{row+1}{chr(65+col)}"
            hint_label = QLabel(f"• {location_str}")
            font = hint_label.font()
            font.setPointSize(12)
            hint_label.setFont(font)
            layout5.addWidget(hint_label)

        mine_section = QLabel("지뢰 셀:")
        mine_section.setStyleSheet("font-weight: bold; color: red;")
        layout5.addWidget(mine_section)
        for hint in mine_hints:
            row, col = hint
            location_str = f"{row+1}{chr(65+col)}"
            hint_label = QLabel(f"• {location_str}")
            font = hint_label.font()
            font.setPointSize(12)
            hint_label.setFont(font)
            layout5.addWidget(hint_label)

        main_layout.addWidget(frame5)







        # Sixth Frame
        frame6 = QFrame()
        layout6 = QVBoxLayout(frame6)

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

        def recapture():
            self.close()
            self.__init__()
            self.show()
        recapture_button.clicked.connect(recapture)
        layout6.addWidget(recapture_button)
        main_layout.addWidget(frame6)



        # Last Frame
        frame_last = QLabel("Bye")
        main_layout.addWidget(frame_last)

        # Fix the window size, position
        screen = QApplication.primaryScreen().geometry()
        window_size = self.sizeHint()
        self.setFixedSize(window_size)
        self.setGeometry(screen.width() - window_size.width(), 30,
                        window_size.width(), window_size.height())





