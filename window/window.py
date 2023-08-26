import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame

import random

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt Example")

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
        grid_layout = QGridLayout()  # Use QGridLayout for a grid arrangement
        grid_layout.setSpacing(0)  # Set spacing to 0 for no gaps
        grid_layout.setContentsMargins(10, 10, 10, 10)
        frame2.setLayout(grid_layout)

        for row in range(8):
            for col in range(8):
                # image_path = f"images/cell_{(row*8 + col)%9+1}.png"
                image_path = f"images/cell_{random.randint(1, 9)}.png"
                pixmap = QPixmap(image_path)
                label = QLabel()
                label.setPixmap(pixmap)
                grid_layout.addWidget(label, row, col)

        # Third Frame
        frame3 = QLabel("Bye")
        main_layout.addWidget(frame3)

        # Fix the window size
        self.setFixedSize(self.sizeHint())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
