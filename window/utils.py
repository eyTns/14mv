import time
from itertools import combinations

import pyautogui
import pygetwindow as gw
from pydantic import BaseModel

from window.const import CLICK_COORDINATES, NEIGHBORS, TOTAL_MINES, INITIAL_POSITIONS
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
    value: int
    mines_needed: int
    total_blanks: int
    blank_cells: set[tuple[int, int]]

    def __eq__(self, other: "Region") -> bool:
        return self.blank_cells == other.blank_cells

    def __sub__(self, other: "Region") -> "Region":
        return Region(
            value=self.value - other.value,
            mines_needed=self.mines_needed - other.mines_needed,
            total_blanks=self.total_blanks - other.total_blanks,
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
            value=grid[row][col],
            mines_needed=mines_needed,
            total_blanks=len(neighboring_blanks),
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
        value=mine_value,
        mines_needed=mines_needed,
        total_blanks=len(blanks),
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
        value=mine_value,
        mines_needed=mines_needed,
        total_blanks=len(blanks),
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


def find_double_areas(regions_info: list[Region]):
    hints = set()

    for i, region1 in enumerate(regions_info):
        for j, region2 in enumerate(regions_info[i + 1 :]):
            blanks1_set = region1.blank_cells
            blanks2_set = region2.blank_cells
            common_blanks = blanks1_set.intersection(blanks2_set)

            if not common_blanks:
                continue

            only_in_cell1 = blanks1_set - blanks2_set
            only_in_cell2 = blanks2_set - blanks1_set

            need1 = region1.mines_needed
            need2 = region2.mines_needed
            blank1 = len(only_in_cell1)
            blank2 = len(only_in_cell2)

            if blank1 <= need1 - need2:
                for blank_r, blank_c in only_in_cell1:
                    hints.add(("mine", (blank_r, blank_c)))
                for blank_r, blank_c in only_in_cell2:
                    hints.add(("safe", (blank_r, blank_c)))

            if blank2 <= need2 - need1:
                for blank_r, blank_c in only_in_cell2:
                    hints.add(("mine", (blank_r, blank_c)))
                for blank_r, blank_c in only_in_cell1:
                    hints.add(("safe", (blank_r, blank_c)))

    return hints


def find_triple_inclusions(regions_info: list[Region]):
    hints = set()

    for i, region1 in enumerate(regions_info):
        for j, region2 in enumerate(regions_info[i + 1 :], i + 1):
            blanks1_set = region1.blank_cells
            blanks2_set = region2.blank_cells
            common_12 = blanks1_set.intersection(blanks2_set)
            if common_12:
                continue

            for k, region3 in enumerate(regions_info):
                if i == k or j == k:
                    continue
                blanks3_set = region3.blank_cells
                common_13 = blanks1_set.intersection(blanks3_set)
                common_23 = blanks2_set.intersection(blanks3_set)
                if not common_13 or not common_23:
                    continue

                newr1 = Region(
                    value=region1.value + region2.value,
                    mines_needed=region1.mines_needed + region2.mines_needed,
                    total_blanks=region1.total_blanks + region2.total_blanks,
                    blank_cells=region1.blank_cells.union(region2.blank_cells),
                )
                newr2 = region3

                only_in_cell1 = newr1.blank_cells - newr2.blank_cells
                only_in_cell2 = newr2.blank_cells - newr1.blank_cells

                need1 = newr1.mines_needed
                need2 = newr2.mines_needed
                blank1 = len(only_in_cell1)
                blank2 = len(only_in_cell2)

                if blank1 <= need1 - need2:
                    for blank_r, blank_c in only_in_cell1:
                        hints.add(("mine", (blank_r, blank_c)))
                    for blank_r, blank_c in only_in_cell2:
                        hints.add(("safe", (blank_r, blank_c)))
                if blank2 <= need2 - need1:
                    for blank_r, blank_c in only_in_cell2:
                        hints.add(("mine", (blank_r, blank_c)))
                    for blank_r, blank_c in only_in_cell1:
                        hints.add(("safe", (blank_r, blank_c)))

    return hints


def find_triple_inequalities(regions_info: list[Region], deep: bool = False):
    hints = set()

    for r1, r2, r3 in combinations(regions_info, 3):
        r1b = r1.blank_cells
        r2b = r2.blank_cells
        r3b = r3.blank_cells
        r1on = r1b - r2b - r3b
        r2on = r2b - r3b - r1b
        r3on = r3b - r1b - r2b
        r1m = r1.mines_needed
        r2m = r2.mines_needed
        r3m = r3.mines_needed
        r1n = r1.total_blanks - r1m
        r2n = r2.total_blanks - r2m
        r3n = r3.total_blanks - r3m

        if r1m - r2m - r3m + 1 >= len(r1on):
            safe_cells = (r2b.intersection(r3b)) - r1b
            if safe_cells:
                for blank_r, blank_c in safe_cells:
                    hints.add(("safe", (blank_r, blank_c)))

        if r2m - r3m - r1m + 1 >= len(r2on):
            safe_cells = (r3b.intersection(r1b)) - r2b
            if safe_cells:
                for blank_r, blank_c in safe_cells:
                    hints.add(("safe", (blank_r, blank_c)))

        if r3m - r1m - r2m + 1 >= len(r3on):
            safe_cells = (r1b.intersection(r2b)) - r3b
            if safe_cells:
                for blank_r, blank_c in safe_cells:
                    hints.add(("safe", (blank_r, blank_c)))

        if r1n - r2n - r3n + 1 >= len(r1on):
            mine_cells = (r2b.intersection(r3b)) - r1b
            if mine_cells:
                for blank_r, blank_c in mine_cells:
                    hints.add(("mine", (blank_r, blank_c)))

        if r2n - r3n - r1n + 1 >= len(r2on):
            mine_cells = (r3b.intersection(r1b)) - r2b
            if mine_cells:
                for blank_r, blank_c in mine_cells:
                    hints.add(("mine", (blank_r, blank_c)))

        if r3n - r1n - r2n + 1 >= len(r3on):
            mine_cells = (r1b.intersection(r2b)) - r3b
            if mine_cells:
                for blank_r, blank_c in mine_cells:
                    hints.add(("mine", (blank_r, blank_c)))

        if deep and hints:
            print(f"Triple hints: {hints}")
            return hints

    return hints


def find_quadruple_inequalities(regions_info: list[Region], deep: bool = False):
    hints = set()

    for r1, r2, r3, r4 in combinations(regions_info, 4):
        r1b = r1.blank_cells
        r2b = r2.blank_cells
        r3b = r3.blank_cells
        r4b = r4.blank_cells
        r1on = r1b - r2b - r3b - r4b
        r2on = r2b - r3b - r4b - r1b
        r3on = r3b - r4b - r1b - r2b
        r4on = r4b - r1b - r2b - r3b
        r1m = r1.mines_needed
        r2m = r2.mines_needed
        r3m = r3.mines_needed
        r4m = r4.mines_needed
        r1n = r1.total_blanks - r1m
        r2n = r2.total_blanks - r2m
        r3n = r3.total_blanks - r3m
        r4n = r4.total_blanks - r4m

        if r1m - r2m - r3m - r4m + 1 >= len(r1on):
            safe23 = r2b.intersection(r3b)
            safe34 = r3b.intersection(r4b)
            safe42 = r4b.intersection(r2b)
            safe_cells = safe23.union(safe34).union(safe42) - r1b
            if safe_cells:
                for blank_r, blank_c in safe_cells:
                    hints.add(("safe", (blank_r, blank_c)))

        if r2m - r3m - r4m - r1m + 1 >= len(r2on):
            safe34 = r3b.intersection(r4b)
            safe41 = r4b.intersection(r1b)
            safe13 = r1b.intersection(r3b)
            safe_cells = safe34.union(safe41).union(safe13) - r2b
            if safe_cells:
                for blank_r, blank_c in safe_cells:
                    hints.add(("safe", (blank_r, blank_c)))

        if r3m - r4m - r1m - r2m + 1 >= len(r3on):
            safe41 = r4b.intersection(r1b)
            safe12 = r1b.intersection(r2b)
            safe24 = r2b.intersection(r4b)
            safe_cells = safe41.union(safe12).union(safe24) - r3b
            if safe_cells:
                for blank_r, blank_c in safe_cells:
                    hints.add(("safe", (blank_r, blank_c)))

        if r4m - r1m - r2m - r3m + 1 >= len(r4on):
            safe12 = r1b.intersection(r2b)
            safe23 = r2b.intersection(r3b)
            safe31 = r3b.intersection(r1b)
            safe_cells = safe12.union(safe23).union(safe31) - r4b
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

        if r2n - r3n - r4n - r1n + 1 >= len(r2on):
            mine34 = r3b.intersection(r4b)
            mine41 = r4b.intersection(r1b)
            mine13 = r1b.intersection(r3b)
            mine_cells = mine34.union(mine41).union(mine13) - r2b
            if mine_cells:
                for blank_r, blank_c in mine_cells:
                    hints.add(("mine", (blank_r, blank_c)))

        if r3n - r4n - r1n - r2n + 1 >= len(r3on):
            mine41 = r4b.intersection(r1b)
            mine12 = r1b.intersection(r2b)
            mine24 = r2b.intersection(r4b)
            mine_cells = mine41.union(mine12).union(mine24) - r3b
            if mine_cells:
                for blank_r, blank_c in mine_cells:
                    hints.add(("mine", (blank_r, blank_c)))

        if r4n - r1n - r2n - r3n + 1 >= len(r4on):
            mine12 = r1b.intersection(r2b)
            mine23 = r2b.intersection(r3b)
            mine31 = r3b.intersection(r1b)
            mine_cells = mine12.union(mine23).union(mine31) - r4b
            if mine_cells:
                for blank_r, blank_c in mine_cells:
                    hints.add(("mine", (blank_r, blank_c)))

        # if deep and hints:
        if hints:
            print(f"Quadruple hints: {hints}")
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


def location_to_cell_coordinates(location, size):
    if size not in INITIAL_POSITIONS:
        raise ValueError("Invalid size. Size should be 5, 6, 7, or 8.")

    row, col = location
    if not (0 <= row < size and 0 <= col < size):
        raise ValueError(
            f"Invalid location. Row and column should be between 0 and {size-1}"
        )

    initial_x, initial_y = INITIAL_POSITIONS[size]
    x_increment, y_increment = 50, 50

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
        relative_x, relative_y = location_to_cell_coordinates(location, size)
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
