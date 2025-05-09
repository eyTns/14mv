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
    all_solved_check,
    PuzzleStatus,
)
from window.hint_utils import (
    find_flag_adjacent_cells,
    find_remaining_cells_from_quad,
    find_single_cell_from_triplet,
)
from window.utils import (
    ExpandedRegion,
    activate_window,
    # analyze_regions,
    apply_hints,
    diff_regions,
    expand_regions,
    find_all_area_hints,
    next_level_check,
    skip_level,
    solve_with_expanded_regions,
    get_grid_region,
    process_hints,
    analyze_exregions_by_rule,
    analyze_exregions_by_right_side_rules,
    get_expanded_regions_by_left_side_rules,
    switch_to_other_size,
    get_rule_regions,
    get_all_rule_regions,
)
import time
from random import shuffle

from window.operate_utils import PuzzleVariant


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
        self.iterate_forever = conf["iterate_forever"]
        self.cell_size = detect_cell_size(self.window_title)

        variant_strings = []
        # rules_to_examine = ["D", "A", "H", "M", "L", "W'", "T"]
        # left_rules = ["Q", "T", "D", "A", "H"]
        # right_rules = ["", "M", "L", "W", "N", "X", "P", "X'", "K", "W'"]
        # rules_to_examine = [i + j for i in left_rules for j in right_rules]
        # shuffle(rules_to_examine)
        # size_to_examine = [5, 6, 7, 8]
        # difficulty_to_examine = ["", "!"]
        # variant_strings.extend(
        #     [
        #         f"{i} {j}{k}"
        #         for j in size_to_examine
        #         for k in difficulty_to_examine
        #         for i in rules_to_examine
        #     ]
        # )

        rules_to_examine = [
            # "AW",
            "AX'",
            "AW'",
            # "BX",
            # "BX'",
            # "BK",
        ]
        size_to_examine = [5]
        difficulty_to_examine = ["", "!"]
        variant_strings.extend(
            [
                f"{i} {j}{k}"
                for j in size_to_examine
                for i in rules_to_examine
                for k in difficulty_to_examine
            ]
        )

        self.variants_to_iterate = [
            PuzzleVariant.from_string(vs) for vs in variant_strings
        ]

        if self.iterate_forever:
            while True:
                next_variant = self.variants_to_iterate.pop(0)
                to_click = next_variant.get_menu_coordinates()
                switch_to_other_size(self.window_title, to_click)
                self.variants_to_iterate.append(next_variant)
                self.cell_size = detect_cell_size(self.window_title)
                self.rule = next_variant.rule
                self.skipped_levels = 0
                while True:
                    self.process_game_data()
                    print("skipping level")
                    skip_level(self.window_title)
                    self.skipped_levels += 1
                    if self.skipped_levels >= 5:
                        break
                    if all_solved_check(self.window_title):
                        break
                print("moving to other size")
        else:
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
            if all_solved_check(self.window_title):
                break
            status = next_level_check(self.window_title, save_path)
            if status == PuzzleStatus.ALREADY_SOLVED:
                print("skipping level")
                self.skipped_levels += 1
                break
            capture_window_screenshot(self.window_title)
            best_fit_cells = find_best_fit_cells(
                self.window_title, self.cell_size, self.rule
            )
            grid = convert_to_numeric(best_fit_cells)
            # if capture_and_stop:
            # for row in grid:
            #     for cell in row:
            #         print(f"{str(cell).rjust(4)}", end=" ")
            #     print()
            # return 1 / 0
            hints_found = False

            def is_regionable(rule):
                regionable_single = ["Q", "C", "T", "O", "D", "S", "T'", "D'", "A", "H"]
                regionable_double = ["V", "B", "X", "X'", "K", "BX", "BX'", "BK"]
                return rule in (regionable_single + regionable_double)

            for include_grid in [False, True]:
                if is_regionable(self.rule):
                    hint_count = 0
                    hints = set()
                    while True:
                        regions = get_all_rule_regions(grid, self.rule)
                        if include_grid:
                            regions.append(get_grid_region(grid, self.rule))
                        hints.update(find_all_area_hints(regions, grid, self.rule))
                        if hint_count < len(hints):
                            hint_count = len(hints)
                            grid = apply_hints(grid, hints)
                            continue
                        break
                    if hints:
                        process_hints(
                            self.window_title, hints, self.cell_size, save_path
                        )
                        hints_found = True
                        break
                    regions = diff_regions(regions)
                    print(f"diff regions: {len(regions)}")
                    hints = find_all_area_hints(regions)
                    if hints:
                        process_hints(
                            self.window_title, hints, self.cell_size, save_path
                        )
                        hints_found = True
                        break
                exregions = analyze_exregions_by_right_side_rules(grid, self.rule)
                regions = get_all_rule_regions(grid, self.rule)
                if include_grid:
                    regions.append(get_grid_region(grid, self.rule))
                exregions.extend(expand_regions(regions, grid, self.rule))
                exregions.extend(
                    get_expanded_regions_by_left_side_rules(grid, self.rule)
                )
                hints = solve_with_expanded_regions(exregions, grid, self.rule)
                if hints:
                    process_hints(self.window_title, hints, self.cell_size, save_path)
                    hints_found = True
                    break
            if not hints_found:
                print("hint not found")
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
