import os
import time

import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import Image, ImageGrab


def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None


def imwrite(filename, img, params=None):
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode="w+b") as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def capture_window_screenshot(window_title):
    try:
        target_window = gw.getWindowsWithTitle(window_title)[0]
        target_window.activate()
        x, y, width, height = (
            target_window.left,
            target_window.top,
            target_window.width,
            target_window.height,
        )
        time.sleep(0.2)
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        screenshot.save(f"{window_title}.png")
        return True
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return False


def find_template_in_screenshot(screenshot_path, template_path):
    try:
        screenshot = Image.open(screenshot_path)
        template = Image.open(template_path)
        screenshot_width, screenshot_height = screenshot.size
        template_width, template_height = template.size
        for x in range(screenshot_width - template_width + 1):
            for y in range(screenshot_height - template_height + 1):
                screenshot_region = screenshot.crop(
                    (x, y, x + template_width, y + template_height)
                )
                if screenshot_region == template:
                    return x, y
        return None

    except Exception as e:
        print(f"Error while searching for template: {e}")
        return None


# Define the size-to-initial-position dictionary
size_to_initial_position_dict = {
    5: (395, 234),
    6: (370, 209),
    7: (345, 184),
    8: (320, 159),
}


def get_cropped_cell_coordinates(size):
    if size not in size_to_initial_position_dict:
        raise ValueError("Invalid size. Size should be 5, 6, 7, or 8.")
    initial_x, initial_y = size_to_initial_position_dict[size]
    x_increment, y_increment = 50, 50
    cell_coordinates = []
    for row in range(size):
        row_coordinates = []
        for col in range(size):
            x1 = initial_x + col * x_increment
            y1 = initial_y + row * y_increment
            x2 = x1 + x_increment
            y2 = y1 + y_increment
            row_coordinates.append((x1, y1, x2, y2))
        cell_coordinates.append(row_coordinates)

    return cell_coordinates


def find_all_templates_in_screenshot(screenshot_path, template_path):
    try:
        screenshot = Image.open(screenshot_path)
        template = Image.open(template_path)
        screenshot_width, screenshot_height = screenshot.size
        template_width, template_height = template.size
        positions = []
        screenshot_region = None
        for x in range(screenshot_width - template_width + 1):
            for y in range(screenshot_height - template_height + 1):
                screenshot_region = screenshot.crop(
                    (x, y, x + template_width, y + template_height)
                )
                if (x, y) in size_to_initial_position_dict.values():
                    screenshot_region.save(f"screenshot_region_{x}_{y}.png")
                if screenshot_region == template:
                    positions.append((x, y))
        return positions
    except Exception as e:
        print(f"Error while searching for templates: {e}")
        return []


def compare_image_same(image_path_1, image_path_2):
    image_1 = Image.open(image_path_1)
    image_2 = Image.open(image_path_2)
    return image_1 == image_2


def MSE_of_images(image_path_1, image_path_2):
    image1 = imread(image_path_1)
    image2 = imread(image_path_2)
    mse = ((image1 - image2) ** 2).mean()
    return mse


def find_best_template_filename(captured_cell_path):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    templates_directory = os.path.join(current_directory, "..", "images")
    best_template_filename = None
    min_mse = float("inf")
    for template_filename in os.listdir(templates_directory):
        mse = MSE_of_images(
            captured_cell_path, os.path.join(templates_directory, template_filename)
        )
        if mse < min_mse:
            min_mse = mse
            best_template_filename = template_filename

    # print(captured_cell_path)
    # print(f'Best template: {best_template_filename}, MSE: {min_mse}')

    if best_template_filename is not None:
        imwrite(
            "best_template.png",
            imread(os.path.join(templates_directory, best_template_filename)),
        )
        return best_template_filename, min_mse
    else:
        return None, None


def find_best_fit_cells(screenshot_path, cell_size):
    cell_coordinates = get_cropped_cell_coordinates(cell_size)
    screenshot = imread(screenshot_path)
    best_fit_filenames = []
    for row in cell_coordinates:
        row_best_fit = []
        for coordinates in row:
            x1, y1, x2, y2 = coordinates
            captured_cell = screenshot[y1:y2, x1:x2]
            temp_dir = "C:/dev/14mv/temp"  ## should not have korean
            captured_cell_filename = os.path.join(
                temp_dir, f"captured_cell_{coordinates[0]}_{coordinates[1]}.png"
            )
            imwrite(captured_cell_filename, captured_cell)
            best_template_filename, min_mse = find_best_template_filename(
                captured_cell_filename
            )
            row_best_fit.append(best_template_filename)
        best_fit_filenames.append(row_best_fit)
    return best_fit_filenames


def convert_to_numeric(best_fit_cells):
    filename_to_numeric = {f"cell_{i}.png": i for i in range(0, 9 + 1)}
    filename_to_numeric.update(
        {"cell_blank.png": -1, "cell_flag.png": -2, "cell_question.png": -3}
    )
    return [[filename_to_numeric[cell] for cell in row] for row in best_fit_cells]


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


def get_neighboring_blanks(row, col, grid):
    neighboring_blanks = []
    mines_to_place = grid[row][col]

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            r, c = row + dr, col + dc

            if 0 <= r < len(grid) and 0 <= c < len(grid[0]) and (r != row or c != col):
                neighbor_value = grid[r][c]

                if neighbor_value == -1:
                    neighboring_blanks.append((r, c))
                elif neighbor_value == -2:
                    mines_to_place -= 1

    return mines_to_place, neighboring_blanks


def analyze_number_cells(grid):
    number_cells_info = {}
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] >= 0:  # 숫자 칸인 경우
                mines_needed, blank_cells = get_neighboring_blanks(r, c, grid)
                if blank_cells:
                    number_cells_info[(r, c)] = {
                        "value": grid[r][c],
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
                hints.append({"type": "safe", "location": (blank_r, blank_c)})
        elif mines_needed == len(blank_cells) and mines_needed > 0:
            for blank_r, blank_c in blank_cells:
                hints.append({"type": "mine", "location": (blank_r, blank_c)})

    return hints


def find_single_clickable_cells(number_cells_info):
    hints = []

    for (r, c), info in number_cells_info.items():
        mines_needed = info["mines_needed"]
        blank_cells = info["blank_cells"]
        if mines_needed == 0 and len(blank_cells) > 0:
            hints.append({"type": "safe", "location": (r, c)})
        elif mines_needed == len(blank_cells) and mines_needed > 0:
            hints.append({"type": "safe", "location": (r, c)})

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
            blankc = len(common_blanks)

            # if (r1, c1) == (4, 2) and (r2, c2) == (5, 2):
            #     print(f"Only in cell 1: {only_in_cell1}")
            #     print(f"Only in cell 2: {only_in_cell2}")
            #     print(f"Common blanks: {common_blanks}")
            #     print(f"Mines needed 1: {need1}")
            #     print(f"Mines needed 2: {need2}")

            if blank1 <= need1 - need2 and need1 > need2:
                for blank_r, blank_c in only_in_cell1:
                    hints.append({"type": "mine", "location": (blank_r, blank_c)})
                for blank_r, blank_c in only_in_cell2:
                    hints.append({"type": "safe", "location": (blank_r, blank_c)})

            if blank2 <= need2 - need1 and need2 > need1:
                for blank_r, blank_c in only_in_cell2:
                    hints.append({"type": "mine", "location": (blank_r, blank_c)})
                for blank_r, blank_c in only_in_cell1:
                    hints.append({"type": "safe", "location": (blank_r, blank_c)})

            if need1 <= need2 - blank2:
                for blank_r, blank_c in only_in_cell1:
                    hints.append({"type": "safe", "location": (blank_r, blank_c)})

            if need1 - blank1 >= need2:
                for blank_r, blank_c in only_in_cell2:
                    hints.append({"type": "safe", "location": (blank_r, blank_c)})

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

        # 각 위치에서 지정된 방식으로 클릭
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

        # 원래 마우스 위치로 복귀
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
        hints: [{'type': 'safe' or 'mine', 'location': (row, col)}, ...] 리스트
        size: 그리드 크기 (5, 6, 7, 8)
    """
    clicks = []
    for hint in hints:
        location = hint["location"]
        relative_x, relative_y = location_to_cell_coordinates(location, size)
        button_type = "left" if hint["type"] == "safe" else "right"
        clicks.append((relative_x, relative_y, button_type))
    return batch_click_positions(window_title, clicks)


def input_spacebar(window_title):
    """
    대상 창을 활성화하고 스페이스바를 입력합니다.
    """
    target_window = gw.getWindowsWithTitle(window_title)[0]
    target_window.activate()
    pyautogui.press("space")
