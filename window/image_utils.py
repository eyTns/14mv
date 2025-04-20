import os
import time
from enum import Enum

import cv2
import numpy as np
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


class PuzzleStatus(Enum):
    FINISH = "Finish"
    NEXT = "Next"
    INCOMPLETE = "Incomplete"


def completed_check(screenshot_path) -> PuzzleStatus:
    """
    스크린샷에서 다음 문제로 넘어갈지 확인합니다.

    Args:
        screenshot_path (str): 스크린샷 이미지 파일 경로
    """
    try:
        screenshot = imread(screenshot_path)
        if screenshot is None:
            return False
        yellow = (0, 255, 255)
        dark_yellow = (0, 178, 178)
        color1 = screenshot[51, 833]
        color2 = screenshot[65, 868]
        color3 = screenshot[70, 863]
        if (color1 == yellow).all() and (color2 == yellow).all():
            return PuzzleStatus.FINISH
        if (color1 == dark_yellow).all and (color3 == dark_yellow).all():
            return PuzzleStatus.NEXT
        return PuzzleStatus.INCOMPLETE

    except Exception as e:
        print(f"Error checking pixel colors: {e}")
        return PuzzleStatus.INCOMPLETE
