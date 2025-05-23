import os
import time
from enum import Enum

import cv2
import numpy as np
import pygetwindow as gw
from PIL import Image, ImageGrab

from window.const import INITIAL_POSITIONS, INITIAL_POSITIONS_2, SPECIAL_CELLS


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
        time.sleep(0.03)
        x, y, width, height = (
            target_window.left,
            target_window.top,
            target_window.width,
            target_window.height,
        )
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        screenshot.save(f"{window_title}.png")
        return True
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return False


def detect_cell_size(window_title):
    capture_window_screenshot(window_title)
    screenshot = imread(f"{window_title}.png")
    gray = (128, 128, 128)
    white = (255, 255, 255)
    for size in [8, 7, 6, 5]:
        if window_title == "Minesweeper Variants":
            x, y = INITIAL_POSITIONS[size]
            color = screenshot[y, x]
            if (color == white).all():
                return size
        elif window_title == "Minesweeper Variants 2":
            x, y = INITIAL_POSITIONS_2[size]
            color = screenshot[y - 1, x - 1]
            if (color > gray).all():
                return size
    raise ValueError("cell_size not found")


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


def get_cropped_cell_coordinates(window_title, size):
    if window_title == "Minesweeper Variants":
        initial_x, initial_y = INITIAL_POSITIONS[size]
        x_increment, y_increment = 50, 50
    elif window_title == "Minesweeper Variants 2":
        initial_x, initial_y = INITIAL_POSITIONS_2[size]
        x_increment, y_increment = 45, 45
    cell_coordinates = []
    for row in range(size):
        row_coordinates = []
        for col in range(size):
            x1 = initial_x + col * x_increment
            y1 = initial_y + row * y_increment
            if window_title == "Minesweeper Variants":
                x2 = x1 + x_increment
                y2 = y1 + y_increment
            elif window_title == "Minesweeper Variants 2":
                x2 = x1 + x_increment - 3
                y2 = y1 + y_increment - 3
            row_coordinates.append((x1, y1, x2, y2))
        cell_coordinates.append(row_coordinates)

    return cell_coordinates


def compare_image_same(image_path_1, image_path_2):
    image_1 = Image.open(image_path_1)
    image_2 = Image.open(image_path_2)
    return image_1 == image_2


def MSE_of_images(image_path_1, image_path_2):
    image1 = imread(image_path_1)
    image2 = imread(image_path_2)
    mse = ((image1 - image2) ** 2).mean()
    return mse


def count_different_pixels(image_path_1, image_path_2):
    image1 = imread(image_path_1)
    image2 = imread(image_path_2)
    diff_mask = np.any(image1 - image2 != 0, axis=2)
    return np.count_nonzero(diff_mask)


def find_best_template_filename(window_title, captured_cell_path, templates_directory):
    best_template_filename = None
    min_measure = float("inf")
    for template_filename in os.listdir(templates_directory):
        template_path = os.path.join(templates_directory, template_filename)
        diff_pixels = count_different_pixels(captured_cell_path, template_path)
        if diff_pixels < min_measure:
            min_measure = diff_pixels
            best_template_filename = template_filename
            if diff_pixels == 0:
                break
        # mse = MSE_of_images(captured_cell_path, template_path)
        # if mse < min_measure:
        #     min_measure = mse
        #     best_template_filename = template_filename

    # if min_diff_pixels > 0:
    #     print(f"min_diff_pixels: {min_diff_pixels}")
    #     print(f"captured_cell_path: {captured_cell_path}")
    #     print(f"best_template_filename: {best_template_filename}")
    #     return 1 / 0

    if best_template_filename is not None:
        imwrite(
            "best_template.png",
            imread(os.path.join(templates_directory, best_template_filename)),
        )
        return best_template_filename, min_measure
    else:
        return None, None


def find_best_fit_cells(window_title, cell_size, rule):
    screenshot_path = f"{window_title}.png"
    cell_coordinates = get_cropped_cell_coordinates(window_title, cell_size)
    screenshot = imread(screenshot_path)
    temp_dir = "C:/dev/14mv/temp"
    current_directory = os.path.dirname(os.path.abspath(__file__))
    if "W" in rule and not "W'" in rule:
        template_folder = "W"
    elif "N" in rule:
        template_folder = "N"
    else:
        template_folder = "V"
    templates_directory = os.path.join(
        current_directory, "..", "images", window_title, template_folder
    )
    best_fit_filenames = [[] for _ in range(len(cell_coordinates))]
    for row_idx, row in enumerate(cell_coordinates):
        for coordinates in row:
            x1, y1, x2, y2 = coordinates
            captured_cell = screenshot[y1:y2, x1:x2]
            captured_cell_filename = os.path.join(
                temp_dir, f"captured_cell_{coordinates[0]}_{coordinates[1]}.png"
            )
            imwrite(captured_cell_filename, captured_cell)
            best_template_filename, _ = find_best_template_filename(
                window_title, captured_cell_filename, templates_directory
            )
            best_fit_filenames[row_idx].append(best_template_filename)
    return best_fit_filenames


def parse_cell_for_numeric(filename):
    if not filename:
        return None
    name = filename.split(".")[0]
    value = name.split("_")[1]

    if value in SPECIAL_CELLS:
        return SPECIAL_CELLS[value]
    return int(value)


def convert_to_numeric(best_fit_cells) -> list[list[int]]:
    return [[parse_cell_for_numeric(cell) for cell in row] for row in best_fit_cells]


class PuzzleStatus(Enum):
    FINISH = "Finish"
    NEXT = "Next"
    INCOMPLETE = "Incomplete"
    STAR_BROKEN = "Star Broken"
    WRONG_POPUP = "Wrong Popup"
    ALREADY_SOLVED = "Already Solved"


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
        # ultimate mode
        red = (0, 0, 255)
        dark_red = (0, 0, 178)
        black = (0, 0, 0)
        color1 = screenshot[51, 833]
        color2 = screenshot[65, 868]
        color3 = screenshot[70, 863]
        if (color1 == yellow).all() and (color2 == yellow).all():
            return PuzzleStatus.FINISH  ## 체크표시
        if (color1 == dark_yellow).all() and (color3 == dark_yellow).all():
            return PuzzleStatus.NEXT
        if (color1 == dark_red).all() and (color3 == dark_red).all():
            return PuzzleStatus.NEXT

        color4 = screenshot[70, 863]
        color5 = screenshot[70, 863]
        if (color4 == red).all() and (color5 == red).all():
            return PuzzleStatus.ALREADY_SOLVED  ## 빨리감기표시

        color_LD = screenshot[580, 41]
        if (color_LD == black).all():
            return PuzzleStatus.STAR_BROKEN

        color_LU = screenshot[112, 89]
        color_RD = screenshot[520, 945]
        popup_border = (126, 126, 126)
        popup_inside = (45, 45, 45)
        if (color_LU == popup_border).all() and (color_RD == popup_inside).all():
            return PuzzleStatus.WRONG_POPUP

        return PuzzleStatus.INCOMPLETE

    except Exception as e:
        print(f"Error checking pixel colors: {e}")
        return PuzzleStatus.INCOMPLETE


def all_solved_check(window_title):
    capture_window_screenshot(window_title)
    current_screenshot = imread(f"{window_title}.png")
    reference_image = imread("size_skipper.png")
    x1, y1, x2, y2 = 946, 571, 1024, 593
    current_region = current_screenshot[y1:y2, x1:x2]
    reference_region = reference_image[y1:y2, x1:x2]
    if current_region.shape == reference_region.shape:
        return np.array_equal(current_region, reference_region)
    else:
        print("Region dimensions don't match")
        return False
