import time
from itertools import combinations

import pyautogui
import pygetwindow as gw
from pydantic import BaseModel
from typing import Iterator


from window.const import (
    CLICK_COORDINATES,
    NEIGHBORS,
    TOTAL_MINES,
    INITIAL_POSITIONS,
    INITIAL_POSITIONS_2,
)
from window.image_utils import (
    PuzzleStatus,
    capture_window_screenshot,
    completed_check,
)


def get_neighboring_cells(row, col, grid):
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            r, c = row + dr, col + dc
            if 0 <= r < len(grid) and 0 <= c < len(grid[0]) and (r != row or c != col):
                neighbors.append(grid[r][c])
    return neighbors


def get_neighboring_cells_with_indices(row, col, grid):
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            r, c = row + dr, col + dc
            if 0 <= r < len(grid) and 0 <= c < len(grid[0]) and (r != row or c != col):
                neighbors.append((grid[r][c], r, c))
    return neighbors


def get_total_mines(rule, cell_size):
    if rule in TOTAL_MINES:
        return TOTAL_MINES[rule][cell_size - 5]
    else:
        return None


class Region(BaseModel):
    mines_needed: int
    blank_cells: set[tuple[int, int]]

    @property
    def total_blanks(self) -> int:
        return len(self.blank_cells)

    @property
    def numbers_needed(self) -> int:
        return self.total_blanks - self.mines_needed

    def __eq__(self, other: "Region") -> bool:
        return self.blank_cells == other.blank_cells

    def __sub__(self, other: "Region") -> "Region":
        return Region(
            mines_needed=self.mines_needed - other.mines_needed,
            blank_cells=self.blank_cells - other.blank_cells,
        )


def get_cell_region(grid, rule, row, col) -> Region:
    """
    주어진 셀의 이웃한 빈 칸들을 찾습니다.

    Args:
        grid (list): 게임 그리드
        rule (str): "V", "X" 등 - 이웃을 찾는 규칙
            V: 주변 8방향의 1칸
            X: 상하좌우 방향으로 1-2칸
        row (int): 현재 셀의 행 번호
        col (int): 현재 셀의 열 번호

    Returns:
        Region:
    """
    mines_needed = grid[row][col]
    neighboring_blanks = set()

    if rule in NEIGHBORS.keys():
        neighbors = NEIGHBORS[rule]
    else:
        raise ValueError(f"Invalid rule. Available rules: {NEIGHBORS.keys()}")

    for dr, dc in neighbors:
        r = row + dr
        c = col + dc
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
            if grid[r][c] == -1:
                neighboring_blanks.add((r, c))
            elif grid[r][c] == -2:
                mines_needed -= 1

    if neighboring_blanks:
        return Region(
            mines_needed=mines_needed,
            blank_cells=neighboring_blanks,
        )
    else:
        return None


def get_grid_region(grid, rule) -> Region:
    mine_value = get_total_mines(rule, len(grid))
    mines_needed = mine_value
    blanks = set()

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == -2:
                mines_needed -= 1
            elif grid[r][c] == -1:
                blanks.add((r, c))

    return Region(
        mines_needed=mines_needed,
        blank_cells=blanks,
    )


def get_row_column_region(grid, rule, row, col) -> Region:
    mine_value = get_total_mines(rule, len(grid)) // len(grid)
    blanks = set()

    cells_to_check = []
    if row is not None:
        mine_value *= row[1] - row[0] + 1
        cells_to_check = [
            (r, c) for r in range(row[0], row[1] + 1) for c in range(len(grid[0]))
        ]
    elif col is not None:
        mine_value *= col[1] - col[0] + 1
        cells_to_check = [
            (r, c) for c in range(col[0], col[1] + 1) for r in range(len(grid))
        ]
    mines_needed = mine_value

    for r, c in cells_to_check:
        if grid[r][c] == -2:
            mines_needed -= 1
        elif grid[r][c] == -1:
            blanks.add((r, c))

    return Region(
        mines_needed=mines_needed,
        blank_cells=blanks,
    )


def analyze_regions(grid, rule) -> list[Region]:
    regions = []

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] >= 0:
                regions.append(get_cell_region(grid, rule, r, c))

    regions.append(get_grid_region(grid, rule))

    if "B" in rule:
        for start in range(len(grid)):
            # single lines
            regions.append(get_row_column_region(grid, rule, (start, start), None))
            regions.append(get_row_column_region(grid, rule, None, (start, start)))

    return [r for r in regions if r]


def find_single_clickable_cells(regions_info: list[Region]):
    hints = set()

    for region in regions_info:
        mines_needed = region.mines_needed
        if region.mines_needed == 0 and len(region.blank_cells) > 0:
            for blank_r, blank_c in region.blank_cells:
                hints.add(("safe", (blank_r, blank_c)))
        elif mines_needed == len(region.blank_cells) > 0:
            for blank_r, blank_c in region.blank_cells:
                hints.add(("mine", (blank_r, blank_c)))

    return hints


def deduce_double_inequalities(r1: Region, r2: Region):
    hints = set()

    r1b = r1.blank_cells
    r2b = r2.blank_cells
    r1on = r1b - r2b
    r1m = r1.mines_needed
    r2m = r2.mines_needed

    if r1m - r2m >= len(r1on):
        for blank_r, blank_c in r2b - r1b:
            hints.add(("safe", (blank_r, blank_c)))
        for blank_r, blank_c in r1b - r2b:
            hints.add(("mine", (blank_r, blank_c)))

    return hints


def find_double_areas(regions_info: list[Region]):
    hints = set()
    for r1, r2 in combinations(regions_info, 2):
        hints = hints.union(deduce_double_inequalities(r1, r2))
        hints = hints.union(deduce_double_inequalities(r2, r1))
    return hints


def find_triple_inclusions(regions_info: list[Region]):
    hints = set()

    for r1, r2, r3 in combinations(regions_info, 3):
        if not r1.blank_cells.intersection(r2.blank_cells):
            r12 = Region(
                mines_needed=r1.mines_needed + r2.mines_needed,
                blank_cells=r1.blank_cells.union(r2.blank_cells),
            )
            hints = hints.union(deduce_double_inequalities(r12, r3))
            hints = hints.union(deduce_double_inequalities(r3, r12))
        if not r2.blank_cells.intersection(r3.blank_cells):
            r23 = Region(
                mines_needed=r2.mines_needed + r3.mines_needed,
                blank_cells=r2.blank_cells.union(r3.blank_cells),
            )
            hints = hints.union(deduce_double_inequalities(r23, r1))
            hints = hints.union(deduce_double_inequalities(r1, r23))
        if not r3.blank_cells.intersection(r1.blank_cells):
            r31 = Region(
                mines_needed=r3.mines_needed + r1.mines_needed,
                blank_cells=r3.blank_cells.union(r1.blank_cells),
            )
            hints = hints.union(deduce_double_inequalities(r31, r2))
            hints = hints.union(deduce_double_inequalities(r2, r31))
    return hints


def deduce_triple_inequalities(r1: Region, r2: Region, r3: Region):
    hints = set()

    r1b = r1.blank_cells
    r2b = r2.blank_cells
    r3b = r3.blank_cells
    r1on = r1b - r2b - r3b
    r1m = r1.mines_needed
    r2m = r2.mines_needed
    r3m = r3.mines_needed
    r1n = r1.numbers_needed
    r2n = r2.numbers_needed
    r3n = r3.numbers_needed

    if r1m - r2m - r3m + 1 >= len(r1on):
        safe_cells = (r2b.intersection(r3b)) - r1b
        if safe_cells:
            for blank_r, blank_c in safe_cells:
                hints.add(("safe", (blank_r, blank_c)))
    if r1n - r2n - r3n + 1 >= len(r1on):
        mine_cells = (r2b.intersection(r3b)) - r1b
        if mine_cells:
            for blank_r, blank_c in mine_cells:
                hints.add(("mine", (blank_r, blank_c)))

    return hints


def find_triple_inequalities(regions_info: list[Region], deep: bool = False):
    hints = set()
    for r1, r2, r3 in combinations(regions_info, 3):
        hints = hints.union(deduce_triple_inequalities(r1, r2, r3))
        hints = hints.union(deduce_triple_inequalities(r2, r3, r1))
        hints = hints.union(deduce_triple_inequalities(r3, r1, r2))
        if deep and hints:
            print(f"Triple hints: {hints}")
            return hints
    return hints


def deduce_quadruple_inequalities(r1: Region, r2: Region, r3: Region, r4: Region):
    hints = set()

    r1b = r1.blank_cells
    r2b = r2.blank_cells
    r3b = r3.blank_cells
    r4b = r4.blank_cells
    r1on = r1b - r2b - r3b - r4b
    r1m = r1.mines_needed
    r2m = r2.mines_needed
    r3m = r3.mines_needed
    r4m = r4.mines_needed
    r1n = r1.numbers_needed
    r2n = r2.numbers_needed
    r3n = r3.numbers_needed
    r4n = r4.numbers_needed

    if r1m - r2m - r3m - r4m + 1 >= len(r1on):
        safe23 = r2b.intersection(r3b)
        safe34 = r3b.intersection(r4b)
        safe42 = r4b.intersection(r2b)
        safe_cells = safe23.union(safe34).union(safe42) - r1b
        if safe_cells:
            for blank_r, blank_c in safe_cells:
                hints.add(("safe", (blank_r, blank_c)))

    if r1n - r2n - r3n - r4n + 1 >= len(r1on):
        mine23 = r2b.intersection(r3b)
        mine34 = r3b.intersection(r4b)
        mine42 = r4b.intersection(r2b)
        mine_cells = mine23.union(mine34).union(mine42) - r1b
        if mine_cells:
            for blank_r, blank_c in mine_cells:
                hints.add(("mine", (blank_r, blank_c)))

    return hints


def find_quadruple_inequalities(regions_info: list[Region], deep: bool = False):
    hints = set()
    for r1, r2, r3, r4 in combinations(regions_info, 4):
        hints = hints.union(deduce_quadruple_inequalities(r1, r2, r3, r4))
        hints = hints.union(deduce_quadruple_inequalities(r2, r3, r4, r1))
        hints = hints.union(deduce_quadruple_inequalities(r3, r4, r1, r2))
        hints = hints.union(deduce_quadruple_inequalities(r4, r1, r2, r3))
        if deep and hints:
            print(f"Quadruple hints: {hints}")
            return hints
    return hints


def find_two_pairs_inequalities(regions_info: list[Region], deep: bool = False):
    hints = set()
    for r1, r2, r3, r4 in combinations(regions_info, 4):
        r1b = r1.blank_cells
        r2b = r2.blank_cells
        r3b = r3.blank_cells
        r4b = r4.blank_cells
        # if not deep:
        #     print(r1b, r2b, r3b, r4b)
        if r1b.intersection(r2b) == r3b.intersection(r4b):
            r12 = Region(
                mines_needed=r1.mines_needed + r2.mines_needed,
                blank_cells=r1.blank_cells.union(r2.blank_cells),
            )
            r34 = Region(
                mines_needed=r3.mines_needed + r4.mines_needed,
                blank_cells=r3.blank_cells.union(r4.blank_cells),
            )
            # if not deep:
            #     print(r12, r34)
            hints = hints.union(deduce_double_inequalities(r12, r34))
            hints = hints.union(deduce_double_inequalities(r34, r12))
        if r1b.intersection(r3b) == r2b.intersection(r4b):
            r13 = Region(
                mines_needed=r1.mines_needed + r3.mines_needed,
                blank_cells=r1.blank_cells.union(r3.blank_cells),
            )
            r24 = Region(
                mines_needed=r2.mines_needed + r4.mines_needed,
                blank_cells=r2.blank_cells.union(r4.blank_cells),
            )
            # if not deep:
            #     print(r13, r24)
            hints = hints.union(deduce_double_inequalities(r13, r24))
            hints = hints.union(deduce_double_inequalities(r24, r13))
        if r1b.intersection(r4b) == r2b.intersection(r3b):
            r14 = Region(
                mines_needed=r1.mines_needed + r4.mines_needed,
                blank_cells=r1.blank_cells.union(r4.blank_cells),
            )
            r23 = Region(
                mines_needed=r2.mines_needed + r3.mines_needed,
                blank_cells=r2.blank_cells.union(r3.blank_cells),
            )
            # if not deep:
            #     print(r14, r23)
            hints = hints.union(deduce_double_inequalities(r14, r23))
            hints = hints.union(deduce_double_inequalities(r23, r14))
        # if deep and hints:
        if hints:
            print(f"Two Pair hints: {hints}")
            return hints
    return hints


def diff_regions(regions: list[Region]):
    while True:
        more_regions = []
        for ri, rj in combinations((regions), 2):
            if ri.total_blanks == rj.total_blanks:
                continue
            elif ri.total_blanks > rj.total_blanks:
                ri, rj = rj, ri
            if ri.blank_cells < rj.blank_cells:
                rk = rj - ri
                if not rk in regions and not rk in more_regions:
                    more_regions.append(rk)
                    if len(regions) + len(more_regions) >= 1000:
                        return regions + more_regions
        if more_regions:
            regions.extend(more_regions)
        else:
            return regions


def apply_hints(grid: list[list[int]], hints):
    for hint_type, (r, c) in hints:
        if hint_type == "safe":
            grid[r][c] = -3
        elif hint_type == "mine":
            grid[r][c] = -2
    return grid


def location_to_cell_coordinates(window_title, location, size):
    row, col = location

    if window_title == "Minesweeper Variants":
        initial_x, initial_y = INITIAL_POSITIONS[size]
        x_increment, y_increment = 50, 50
    elif window_title == "Minesweeper Variants 2":
        initial_x, initial_y = INITIAL_POSITIONS_2[size]
        x_increment, y_increment = 45, 45

    x1 = initial_x + col * x_increment
    y1 = initial_y + row * y_increment
    x2 = x1 + x_increment // 2
    y2 = y1 + y_increment // 2
    return (x2, y2)


def activate_window(window_title):
    target_window = gw.getWindowsWithTitle(window_title)[0]
    target_window.activate()
    time.sleep(0.2)
    return True


def click_positions(window_title, clicks):
    try:
        target_window = gw.getWindowsWithTitle(window_title)[0]
        target_window.activate()
        original_x, original_y = pyautogui.position()
        pyautogui.FAILSAFE = False
        pyautogui.MINIMUM_DURATION = 0
        pyautogui.PAUSE = 0.0001
        # pyautogui.PAUSE = 0.3

        base_x = target_window.left
        base_y = target_window.top
        clicks.append(CLICK_COORDINATES["safe_click"])
        pyautogui.moveTo(base_x + 150, base_y + 150)
        for relative_x, relative_y, button_type in clicks:
            absolute_x = base_x + relative_x
            absolute_y = base_y + relative_y
            pyautogui.moveTo(absolute_x, absolute_y)
            pyautogui.click(button=button_type)

        pyautogui.moveTo(original_x, original_y)
        pyautogui.FAILSAFE = True

        return True

    except Exception as e:
        print(f"Error clicking positions: {e}")
        return False


def click_hints(window_title, hints, size):
    clicks = []
    for hint in hints:
        location = hint[1]
        relative_x, relative_y = location_to_cell_coordinates(
            window_title, location, size
        )
        button_type = "left" if hint[0] == "safe" else "right"
        clicks.append((relative_x, relative_y, button_type))
    return click_positions(window_title, clicks)


def input_spacebar(window_title):
    target_window = gw.getWindowsWithTitle(window_title)[0]
    target_window.activate()
    pyautogui.press("space")


def next_level_check(window_title, save_path):
    capture_window_screenshot(window_title)
    status = completed_check(save_path)
    if status == PuzzleStatus.FINISH:
        input_spacebar(window_title)
        click_positions(window_title, [CLICK_COORDINATES["next_level"]])
    elif status == PuzzleStatus.NEXT:
        click_positions(window_title, [CLICK_COORDINATES["next_level"]])


def skip_level(window_title):
    skip1 = CLICK_COORDINATES["skip_button"]
    skip2 = CLICK_COORDINATES["confirm_skip"]
    click_positions(window_title, [skip1, skip2])
