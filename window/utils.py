import pygetwindow as gw
from PIL import Image, ImageGrab


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

                if (x, y) == (370, 209):
                    screenshot_region.save(f"screenshot_region.png")
                    template.save(f"template.png")
                    
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

