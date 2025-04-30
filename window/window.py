from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from window.image_utils import (
    capture_window_screenshot,
    convert_to_numeric,
    detect_cell_size,
    find_best_fit_cells,
)
from window.utils import (
    activate_window,
    analyze_regions,
    apply_hints,
    click_hints,
    diff_regions,
    expand_regions,
    find_double_areas,
    find_flag_adjacent_cells,
    find_quadruple_inequalities,
    find_remaining_cells_from_quad,
    find_single_cell_from_triplet,
    find_single_clickable_cells,
    find_triple_inclusions,
    find_triple_inequalities,
    find_two_pairs_inequalities,
    get_quad_expanded_regions,
    get_triplet_expanded_regions,
    next_level_check,
    skip_level,
    solve_with_expanded_regions,
)


class HeaderFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("Hello")
        layout.addWidget(label)


class ScreenshotFrame(QFrame):
    def __init__(self, window_title, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        label = QLabel()
        label.setPixmap(QPixmap(f"{window_title}.png"))
        layout.addWidget(label)


class TextFrame(QFrame):
    def __init__(self, conf, parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        self.setLayout(layout)

        self.window_title_edit = QLineEdit(conf["window_title"])
        self.rule_edit = QLineEdit(conf["rule"])

        layout.addWidget(QLabel("Window Title:"), 0, 0)
        layout.addWidget(self.window_title_edit, 0, 1)
        layout.addWidget(QLabel("Rule:"), 1, 0)
        layout.addWidget(self.rule_edit, 1, 1)

        self.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                color: #333333;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
        """
        )

    def get_current_values(self):
        return {
            "window_title": self.window_title_edit.text(),
            "rule": self.rule_edit.text(),
        }


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
    def __init__(self, conf: dict[str, str]):
        super().__init__()

        self.conf = conf
        self.update_config_values()
        self.window_title = conf["window_title"]
        self.rule = conf["rule"].upper()
        self.cell_size = detect_cell_size(self.window_title)

        # # iterate forever
        # while True:
        #     self.process_game_data()
        #     print("skipping level")
        #     skip_level(self.window_title)

        self.process_game_data()

        self.setWindowTitle("14mv solve")
        self.setup_ui()
        self.setup_window_geometry()

    def update_config_values(self):
        self.window_title = self.conf["window_title"]
        self.rule = self.conf["rule"].upper()
        self.cell_size = detect_cell_size(self.window_title)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.header_frame = HeaderFrame()
        self.screenshot_frame = ScreenshotFrame(self.window_title)
        self.text_frame = TextFrame(self.conf)
        self.control_frame = ControlFrame(self.start_new_process)

        main_layout.addWidget(self.header_frame)
        main_layout.addWidget(self.screenshot_frame)
        main_layout.addWidget(self.text_frame)
        main_layout.addWidget(self.control_frame)

    def process_game_data(self):
        save_path = f"{self.window_title}.png"
        activate_window(self.window_title)

        while True:
            capture_window_screenshot(self.window_title)
            best_fit_cells = find_best_fit_cells(self.window_title, self.cell_size)
            grid = convert_to_numeric(best_fit_cells)
            hints = set()
            hint_count = len(hints)

            # 초기 힌트 재귀적 적용
            while True:
                regions = analyze_regions(grid, self.rule)
                hints.update(find_single_clickable_cells(regions))
                if self.rule == "UW":
                    hints.update(find_flag_adjacent_cells(grid))
                if "Q" in self.rule:
                    hints.update(find_remaining_cells_from_quad(grid))
                if "T" in self.rule:
                    hints.update(find_single_cell_from_triplet(grid))
                hints.update(find_double_areas(regions))
                hints.update(find_triple_inclusions(regions))
                hints.update(find_triple_inequalities(regions))
                hints.update(find_quadruple_inequalities(regions[:80]))
                hints.update(find_two_pairs_inequalities(regions[:80]))
                if hint_count < len(hints):
                    hint_count = len(hints)
                    grid = apply_hints(grid, hints)
                    continue
                break
            if hints:
                click_hints(self.window_title, hints, self.cell_size)
                next_level_check(self.window_title, save_path)
                continue

            # 영역 경우의 수 확장
            print("searching expanded regions...")
            # regions = analyze_regions(grid, self.rule, False)
            regions = analyze_regions(grid, self.rule)
            eregions = expand_regions(regions, grid, self.rule)
            if "Q" in self.rule:
                eregions.extend(get_quad_expanded_regions(grid))
            if "T" in self.rule:
                eregions.extend(get_triplet_expanded_regions(grid))
            hints = solve_with_expanded_regions(eregions)
            if hints:
                print(f"{len(hints)} hints found")
                # print(hints)
                click_hints(self.window_title, hints, self.cell_size)
                next_level_check(self.window_title, save_path)
                continue

            # 영역 차집합 포함
            regions = diff_regions(regions)
            print(f"diff regions: {len(regions)}")
            hints = set()
            hints.update(find_single_clickable_cells(regions))
            hints.update(find_double_areas(regions))
            if not hints:
                print("searching more triples...")
                hints = hints.union(find_triple_inequalities(regions[:150], deep=True))
            if not hints:
                print("searching more quadruples...")
                hints = hints.union(
                    find_quadruple_inequalities(regions[:50], deep=True)
                )
            if not hints:
                print("searching more two pairs...")
                hints = hints.union(
                    find_two_pairs_inequalities(regions[:50], deep=True)
                )
            if hints:
                print(f"{len(hints)} hints found")
                click_hints(self.window_title, hints, self.cell_size)
                next_level_check(self.window_title, save_path)
                continue

            break

    def start_new_process(self):
        if hasattr(self, "text_frame"):
            self.conf = self.text_frame.get_current_values()
            self.update_config_values()

        self.process_game_data()

        if hasattr(self, "screenshot_frame"):
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
