import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
from window.utils import capture_window_screenshot, find_all_templates_in_screenshot, find_best_fit_cells

import random

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("random number displayer")

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

        frame4 = QFrame()
        layout = QVBoxLayout()
        # label = QLabel()
        # label.setText("\n".join("Row {}: {}".format(i, ", ".join(cell for cell in row if cell is not None)) for i, row in enumerate(best_fit_cells)))
        # layout.addWidget(label)

        # Create a QTableWidget with 6 rows and 6 columns
        table = QTableWidget(6, 6)
        for i, row in enumerate(best_fit_cells):
            for j, cell in enumerate(row):
                item = QTableWidgetItem(cell)
                table.setItem(i, j, item)
        layout.addWidget(table)
        frame4.setLayout(layout)
        main_layout.addWidget(frame4)








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


        # Last Frame
        frame_last = QLabel("Bye")
        main_layout.addWidget(frame_last)

        # Fix the window size
        self.setFixedSize(self.sizeHint())



