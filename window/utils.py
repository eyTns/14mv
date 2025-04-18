import time

import pyautogui
import pygetwindow as gw
from window.image_utils import imread


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
        mines_to_place = [0,0,0,0,0,10,14,20,26][len(grid)]
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c] == -2:
                    mines_to_place -= 1
                elif grid[r][c] == -1:
                    neighboring_blanks.append((r, c))
        return mines_to_place, neighboring_blanks

    mines_to_place = grid[row][col]

    if rule == "V":
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
    elif rule == "X":
        directions = [
            (-1, 0),
            (-2, 0),
            (1, 0),
            (2, 0),
            (0, -1),
            (0, -2),
            (0, 1),
            (0, 2),
        ]
    elif rule == "X'":
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]
    elif rule == "K":
        directions = [
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        ]
    else:
        raise ValueError("Invalid rule. Available rules: 'V', 'X', 'X'', 'K'")

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
            "value": [0,0,0,0,0,10,14,20,26][len(grid)],
            "mines_needed": mines_needed,
            "total_blanks": len(blank_cells),
            "blank_cells": blank_cells,
        }

    return number_cells_info


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


def find_single_clickable_cells(number_cells_info):
    hints = []

    for (r, c), info in number_cells_info.items():
        mines_needed = info["mines_needed"]
        blank_cells = info["blank_cells"]
        if mines_needed == 0 and len(blank_cells) > 0:
            hints.append(("safe", (r, c)))
        elif mines_needed == len(blank_cells) and mines_needed > 0:
            hints.append(("safe", (r, c)))

    return hints


def find_common_areas(number_cells_info):
    hints = []

    for (r1, c1), info1 in number_cells_info.items():
        for (r2, c2), info2 in number_cells_info.items():
            if (r1, c1) >= (r2, c2):
                continue

            blanks1_set = set(info1["blank_cells"])
            blanks2_set = set(info2["blank_cells"])
            common_blanks = blanks1_set.intersection(blanks2_set)

            if not common_blanks:
                continue

            only_in_cell1 = blanks1_set - blanks2_set
            only_in_cell2 = blanks2_set - blanks1_set

            need1 = info1["mines_needed"]
            need2 = info2["mines_needed"]
            blank1 = len(blanks1_set - blanks2_set)
            blank2 = len(blanks2_set - blanks1_set)

            if blank1 <= need1 - need2:
                for blank_r, blank_c in only_in_cell1:
                    hints.append(("mine", (blank_r, blank_c)))
                for blank_r, blank_c in only_in_cell2:
                    hints.append(("safe", (blank_r, blank_c)))

            if blank2 <= need2 - need1:
                for blank_r, blank_c in only_in_cell2:
                    hints.append(("mine", (blank_r, blank_c)))
                for blank_r, blank_c in only_in_cell1:
                    hints.append(("safe", (blank_r, blank_c)))

    return hints


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


def next_level(window_title):
    input_spacebar(window_title)
    click_window_position(window_title, 564, 484)
