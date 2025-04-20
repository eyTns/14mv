import time

import pyautogui
import pygetwindow as gw
from pydantic import BaseModel
from itertools import combinations

from window.image_utils import (
    PuzzleStatus,
    capture_window_screenshot,
    completed_check,
    size_to_initial_position_dict,
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
    if rule in ["V", "X", "X'", "K"]:
        return [0, 0, 0, 0, 0, 10, 14, 20, 26][cell_size]
    elif rule in ["B", "BX"]:
        return [0, 0, 0, 0, 0, 10, 12, 21, 24][cell_size]
    return None


class Region(BaseModel):
    value: int
    mines_needed: int
    total_blanks: int
    blank_cells: set[tuple[int, int]]

    def __eq__(self, other):
        if not isinstance(other, Region):
            return False
        return self.blank_cells == other.blank_cells

    def __sub__(self, other):
        if not isinstance(other, Region):
            return NotImplemented
        return Region(
            value=self.value - other.value,
            mines_needed=self.mines_needed - other.mines_needed,
            total_blanks=self.total_blanks - other.total_blanks,
            blank_cells=self.blank_cells - other.blank_cells,
        )


DIRECTIONS = {
    "V": [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
    "X": [(-2, 0), (-1, 0), (1, 0), (2, 0), (0, -2), (0, -1), (0, 1), (0, 2)],
    "X'": [(-1, 0), (1, 0), (0, -1), (0, 1)],
    "K": [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
    "B": [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)],
    "BX": [(-2, 0), (-1, 0), (1, 0), (2, 0), (0, -2), (0, -1), (0, 1), (0, 2)],
}


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

    if rule in ["V", "X", "X'", "K", "B", "BX"]:
        directions = DIRECTIONS[rule]
    else:
        raise ValueError(f"Invalid rule. Available rules: {DIRECTIONS.keys()}")

    for dr, dc in directions:
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
    """
    주어진 그리드 전체에서 빈 칸들을 찾습니다.

    Args:
        grid (list): 게임 그리드
        rule (str): "V", "X" 등 - 이웃을 찾는 규칙
            V: 주변 8방향의 1칸
            X: 상하좌우 방향으로 1-2칸

    Returns:
        Region
    """
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
    """
    주어진 행 또는 열에서 빈 칸들을 찾습니다.

    Args:
        grid (list): 게임 그리드
        rule (str): "V", "X" 등 - 이웃을 찾는 규칙
            V: 주변 8방향의 1칸
            X: 상하좌우 방향으로 1-2칸
        row (int | None): 현재 셀의 행 번호
        col (int | None): 현재 셀의 열 번호

    Returns:
        Region
    """
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


def get_neighboring_blanks(grid, rule, row, col):
    """
    주어진 셀의 이웃한 빈 칸들을 찾습니다.

    Args:
        grid (list): 게임 그리드
        rule (str): "V" 또는 "X" - 이웃을 찾는 규칙
            V: 주변 8방향의 1칸
            X: 상하좌우 방향으로 1-2칸
        row (int): 현재 셀의 행 번호 (-1인 경우 전체 그리드 검사)
        col (int): 현재 셀의 열 번호 (-1인 경우 전체 그리드 검사)

    Returns:
        tuple: (남은 지뢰 수, 이웃한 빈 칸들의 위치 목록)
    """
    neighboring_blanks = []

    if row == -1 and col == -1:
        mines_to_place = get_total_mines(rule, len(grid))
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c] == -2:
                    mines_to_place -= 1
                elif grid[r][c] == -1:
                    neighboring_blanks.append((r, c))
        return mines_to_place, neighboring_blanks

    mines_to_place = grid[row][col]

    if rule in ["V", "X", "X'", "K", "B", "BX"]:
        directions = DIRECTIONS[rule]
    else:
        raise ValueError(f"Invalid rule. Available rules: {DIRECTIONS.keys()}")

    for dr, dc in directions:
        r = row + dr
        c = col + dc
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
            if grid[r][c] == -1:
                neighboring_blanks.append((r, c))
            elif grid[r][c] == -2:
                mines_to_place -= 1

    return mines_to_place, neighboring_blanks


def analyze_number_cells(grid, rule):
    number_cells_info = {}

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] >= 0:
                mines_needed, blank_cells = get_neighboring_blanks(grid, rule, r, c)
                if blank_cells:
                    number_cells_info[(r, c)] = {
                        "value": grid[r][c],
                        "mines_needed": mines_needed,
                        "total_blanks": len(blank_cells),
                        "blank_cells": blank_cells,
                    }

    mines_needed, blank_cells = get_neighboring_blanks(grid, rule, -1, -1)
    if blank_cells:
        number_cells_info[(-1, -1)] = {
            "value": get_total_mines(rule, len(grid)),
            "mines_needed": mines_needed,
            "total_blanks": len(blank_cells),
            "blank_cells": blank_cells,
        }

    return number_cells_info


def analyze_regions(grid, rule) -> list[Region]:
    regions = []

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] >= 0:
                regions.append(get_cell_region(grid, rule, r, c))

    regions.append(get_grid_region(grid, rule))

    if rule in ["B", "BX"]:
        for rs, re in combinations(range(len(grid)), 2):
            regions.append(get_row_column_region(grid, rule, (rs, re), None))
        for cs, ce in combinations(range(len(grid[0])), 2):
            regions.append(get_row_column_region(grid, rule, None, (cs, ce)))

    return [r for r in regions if r]


def find_single_cell_hints(number_cells_info):
    hints = []

    for (r, c), info in number_cells_info.items():
        mines_needed = info["mines_needed"]
        blank_cells = info["blank_cells"]

        if mines_needed == 0 and len(blank_cells) > 0:
            for blank_r, blank_c in blank_cells:
                hints.append(("safe", (blank_r, blank_c)))
        elif mines_needed == len(blank_cells) and mines_needed > 0:
            for blank_r, blank_c in blank_cells:
                hints.append(("mine", (blank_r, blank_c)))

    return hints


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


def find_common_areas(regions_info: list[Region]):
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


def find_triple_areas(regions_info: list[Region]):
    hints = set()

    for i, region1 in enumerate(regions_info):
        for j, region2 in enumerate(regions_info[i + 1 :], i + 1):
            blanks1_set = region1.blank_cells
            blanks2_set = region2.blank_cells
            common_12 = blanks1_set.intersection(blanks2_set)
            if common_12:
                continue

            # print("*****", i, j)

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
                if hints:
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


def location_to_cell_coordinates(location, size):
    """
    Convert a location (row, col) to cell coordinates (x, y)

    Args:
        location: tuple of (row, col)
        size: integer representing the grid size (5, 6, 7, or 8)

    Returns:
        tuple: (x, y) coordinates of the center of the cell
    """
    if size not in size_to_initial_position_dict:
        raise ValueError("Invalid size. Size should be 5, 6, 7, or 8.")

    row, col = location
    if not (0 <= row < size and 0 <= col < size):
        raise ValueError(
            f"Invalid location. Row and column should be between 0 and {size-1}"
        )

    initial_x, initial_y = size_to_initial_position_dict[size]
    x_increment, y_increment = 50, 50

    x1 = initial_x + col * x_increment
    y1 = initial_y + row * y_increment
    x2 = x1 + x_increment // 2
    y2 = y1 + y_increment // 2
    return (x2, y2)


def click_window_position(window_title, relative_x, relative_y, right_click=False):
    """
    창을 활성화하고 지정된 상대 좌표를 클릭합니다.

    Args:
        window_title (str): 대상 창의 제목
        relative_x (int): 창 내부의 x 좌표
        relative_y (int): 창 내부의 y 좌표
        right_click (bool): True면 우클릭, False면 좌클릭
    """
    try:
        target_window = gw.getWindowsWithTitle(window_title)[0]
        target_window.activate()
        time.sleep(0.1)
        absolute_x = target_window.left + relative_x
        absolute_y = target_window.top + relative_y
        original_x, original_y = pyautogui.position()
        pyautogui.FAILSAFE = False
        pyautogui.moveTo(absolute_x, absolute_y)
        if right_click:
            pyautogui.rightClick()
        else:
            pyautogui.click()
        pyautogui.moveTo(target_window.left + 100, target_window.top + 100)
        pyautogui.moveTo(original_x, original_y)
        pyautogui.FAILSAFE = True
        return True
    except Exception as e:
        print(f"Error clicking position: {e}")
        return False


def batch_click_positions(window_title, clicks):
    """
    창을 활성화하고 여러 위치를 지정된 방식으로 클릭합니다.

    Args:
        window_title (str): 대상 창의 제목
        click_info_list (list of tuples): [(x, y, button_type), ...] 형식의 목록
            - x, y: 창 내부의 상대 좌표
            - button_type: "left" 또는 "right" 문자열
    """
    try:
        target_window = gw.getWindowsWithTitle(window_title)[0]
        target_window.activate()
        time.sleep(0.1)
        original_x, original_y = pyautogui.position()
        pyautogui.FAILSAFE = False

        for relative_x, relative_y, button_type in clicks:
            absolute_x = target_window.left + relative_x
            absolute_y = target_window.top + relative_y
            pyautogui.moveTo(absolute_x, absolute_y)

            if button_type == "left":
                pyautogui.click()
            elif button_type == "right":
                pyautogui.rightClick()
            else:
                print(f"Warning: Unknown button type '{button_type}', skipping click")

        pyautogui.moveTo(target_window.left + 100, target_window.top + 100)
        pyautogui.moveTo(original_x, original_y)
        pyautogui.FAILSAFE = True

        return True

    except Exception as e:
        print(f"Error clicking positions: {e}")
        return False


def click_cell(window_title, location, size, right_click=False):
    """
    주어진 location의 셀을 클릭합니다.

    Args:
        location: (row, col) 튜플
        size: 그리드 크기 (5,6,7,8)
        right_click: True면 우클릭, False면 좌클릭
    """
    coords = location_to_cell_coordinates(location, size)
    return click_window_position(window_title, coords[0], coords[1], right_click)


def click_hints(window_title, hints, size):
    """
    여러 힌트를 클릭합니다.

    Args:
        hints: [('safe' or 'mine', (row, col)), ...] 리스트
        size: 그리드 크기 (5, 6, 7, 8)
    """
    clicks = []
    for hint in hints:
        location = hint[1]
        relative_x, relative_y = location_to_cell_coordinates(location, size)
        button_type = "left" if hint[0] == "safe" else "right"
        clicks.append((relative_x, relative_y, button_type))
    return batch_click_positions(window_title, clicks)


def input_spacebar(window_title):
    """
    대상 창을 활성화하고 스페이스바를 입력합니다.
    """
    target_window = gw.getWindowsWithTitle(window_title)[0]
    target_window.activate()
    pyautogui.press("space")


def next_level_check(window_title, save_path):
    capture_window_screenshot(window_title)
    status = completed_check(save_path)
    if status == PuzzleStatus.FINISH:
        input_spacebar(window_title)
        click_window_position(window_title, 564, 484)
    elif status == PuzzleStatus.NEXT:
        click_window_position(window_title, 564, 484)
