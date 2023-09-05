import pygetwindow as gw
from PIL import Image, ImageGrab
import cv2
import os
import tempfile


def capture_window_screenshot(window_title, save_path):
    try:
        # Find the window by title
        target_window = gw.getWindowsWithTitle(window_title)[0]

        target_window.activate()

        # Get the window's position and size
        x, y, width, height = target_window.left, target_window.top, target_window.width, target_window.height

        # Capture screenshot
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))

        # Save the screenshot
        screenshot.save(save_path)
        return True
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return False


def find_template_in_screenshot(screenshot_path, template_path):
    try:
        # Load the screenshot and template image
        screenshot = Image.open(screenshot_path)
        template = Image.open(template_path)

        # Get the dimensions
        screenshot_width, screenshot_height = screenshot.size
        template_width, template_height = template.size

        # Iterate over possible positions
        for x in range(screenshot_width - template_width + 1):
            for y in range(screenshot_height - template_height + 1):
                # Crop the screenshot to the same size as the template
                screenshot_region = screenshot.crop((x, y, x + template_width, y + template_height))

                # Compare the cropped region with the template
                if screenshot_region == template:
                    # Return the position of the template image
                    return x, y

        # If no match is found, return None
        return None

    except Exception as e:
        print(f"Error while searching for template: {e}")
        return None


# Define the size-to-initial-position dictionary
size_to_initial_position_dict = {
    5: (395, 234),
    6: (370, 209),
    7: (345, 184),
    8: (320, 159)
}


def get_cropped_cell_coordinates(size):
    # Check if the provided size is valid
    if size not in size_to_initial_position_dict:
        raise ValueError("Invalid size. Size should be 5, 6, 7, or 8.")

    # Get the initial position based on the provided size
    initial_x, initial_y = size_to_initial_position_dict[size]

    # Define the fixed increments
    x_increment, y_increment = 50, 50

    # Initialize a list to store the coordinates of cropped cells
    cell_coordinates = []

    # Calculate the coordinates for all cropped cells
    for row in range(size):
        row_coordinates = []  # Inner list for each row
        for col in range(size):
            x1 = initial_x + col * x_increment
            y1 = initial_y + row * y_increment
            x2 = x1 + x_increment
            y2 = y1 + y_increment
            row_coordinates.append((x1, y1, x2, y2))
        cell_coordinates.append(row_coordinates)  # Append row to the list

    return cell_coordinates


def find_all_templates_in_screenshot(screenshot_path, template_path):
    try:
        # Load the screenshot and template image
        screenshot = Image.open(screenshot_path)
        template = Image.open(template_path)

        # Get the dimensions
        screenshot_width, screenshot_height = screenshot.size
        template_width, template_height = template.size

        # List to store positions of all matches
        positions = []

        screenshot_region = None
        # Iterate over possible positions
        for x in range(screenshot_width - template_width + 1):
            for y in range(screenshot_height - template_height + 1):
                # Crop the screenshot to the same size as the template
                screenshot_region = screenshot.crop((x, y, x + template_width, y + template_height))

                if (x, y) in size_to_initial_position_dict.values():
                    screenshot_region.save(f"screenshot_region_{x}_{y}.png")
                    
                # Compare the cropped region with the template
                if screenshot_region == template:
                    # Add the position of the template image to the list
                    positions.append((x, y))
        
        # Return the list of positions
        return positions
    except Exception as e:
        print(f"Error while searching for templates: {e}")
        return []


def compare_image_same(image_path_1, image_path_2):
    image_1 = Image.open(image_path_1)
    image_2 = Image.open(image_path_2)

    return image_1==image_2


def MSE_of_images(image_path_1, image_path_2):
    # Load the two images you want to compare
    image1 = cv2.imread(image_path_1)
    image2 = cv2.imread(image_path_2)

    # Calculate the Mean Squared Error (MSE)
    mse = ((image1 - image2) ** 2).mean()

    print(f'Mean Squared Error: {mse}')
    return mse


def find_best_template_filename(captured_cell_path):
    # Load the captured cell image
    captured_cell = cv2.imread(captured_cell_path)

    # Construct the full path to the directory where template images are located
    current_directory = os.path.dirname(os.path.abspath(__file__))
    templates_directory = os.path.join(current_directory, '..', 'images')

    # Initialize variables to keep track of the best template and its MSE
    best_template_filename = None
    min_mse = float('inf')

    # Iterate through all template images in the directory
    for template_filename in os.listdir(templates_directory):
        # Load the template image
        template = cv2.imread(os.path.join(templates_directory, template_filename))

        # Calculate the Mean Squared Error (MSE) between the captured cell and the template
        mse = ((captured_cell - template) ** 2).mean()

        # Check if this template has a lower MSE than the current minimum
        if mse < min_mse:
            min_mse = mse
            best_template_filename = template_filename

    # If a best template was found, return its filename and the MSE
    if best_template_filename is not None:
        cv2.imwrite('best_template.png', cv2.imread(os.path.join(templates_directory, best_template_filename)))
        return best_template_filename, min_mse
    else:
        return None, None


def find_best_fit_cells(screenshot_path, cell_size):
    # Get the cropped cell coordinates for the specified size
    cell_coordinates = get_cropped_cell_coordinates(cell_size)

    # Load the screenshot image
    screenshot = cv2.imread(screenshot_path)

    current_directory = os.path.dirname(os.path.abspath(__file__))
    templates_directory = os.path.join(current_directory, '..', 'images')

    # Initialize a list to store the best-fit cell filenames
    best_fit_filenames = []

    # Iterate through the cropped cell coordinates and find the best-fit templates
    for row in cell_coordinates:
        row_best_fit = []  # List to store best-fit template filenames for the row
        for coordinates in row:
            # Crop the cell from the screenshot
            x1, y1, x2, y2 = coordinates
            captured_cell = screenshot[y1:y2, x1:x2]

            # Save the captured cell as an image with a unique name
            temp_dir = tempfile.gettempdir()
            captured_cell_filename = os.path.join(temp_dir, f'captured_cell_{coordinates[0]}_{coordinates[1]}.png')
            cv2.imwrite(captured_cell_filename, captured_cell)

            # Find the best template for the captured cell
            best_template_filename, min_mse = find_best_template_filename(captured_cell_filename)
            row_best_fit.append(best_template_filename)

        best_fit_filenames.append(row_best_fit)

    return best_fit_filenames




