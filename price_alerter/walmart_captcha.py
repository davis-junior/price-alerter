import pathlib
import random
import time
import traceback

import cv2
import numpy as np
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver

from constants import SCRIPT_DIR
from cv2_utils import compare_images, get_black_to_white_ratio


OPEN_RECTANGLE_IMAGE = cv2.imread(
    str(pathlib.Path(SCRIPT_DIR) / "walmart_captcha_images" / "open_rectangle.png")
)

RECTANGLE_FILLED_WAITING_IMAGE = cv2.imread(
    str(
        pathlib.Path(SCRIPT_DIR)
        / "walmart_captcha_images"
        / "rectangle_filled_waiting.png"
    )
)

RECTANGLE_FILLED_FULL_CHECKMARK_IMAGE = cv2.imread(
    str(
        pathlib.Path(SCRIPT_DIR)
        / "walmart_captcha_images"
        / "rectangle_filled_full_checkmark.png"
    )
)

FILLED_RECTANGLE_HALF_CHECKMARK_IMAGE = cv2.imread(
    str(
        pathlib.Path(SCRIPT_DIR)
        / "walmart_captcha_images"
        / "filled_rectangle_half_checkmark.png"
    )
)


def get_walmart_captcha_status(image):
    internal_status = get_walmart_captcha_internal_status(image)
    print(internal_status)

    if internal_status == "OPEN_RECTANGLE":
        return "NOT_STARTED"
    elif internal_status == "RECTANGLE_FILLED_WAITING":
        return "COMPLETE"
    elif internal_status == "RECTANGLE_FILLED_FULL_CHECKMARK":
        return "COMPLETE"
    elif internal_status == "RECTANGLE_FILLED_HALF_CHECKMARK":
        return "COMPLETE"
    elif internal_status == "RECTANGLE_PARTIALLY_FILLED":
        return "IN_PROGRESS"
    elif internal_status == "UNKNOWN_RECTANGLE":
        return "NOT_STARTED"
    elif internal_status == "UNKNOWN":
        return "UNKNOWN"

    return "UNKNOWN"


def get_walmart_captcha_internal_status(image):
    if image is None:
        return "UNKNOWN"

    black_to_white_ratio = get_black_to_white_ratio(image)
    print(f"black_to_white_ratio: {black_to_white_ratio}")

    open_rectangle_matches = compare_images(image, OPEN_RECTANGLE_IMAGE)
    if open_rectangle_matches >= 70 and black_to_white_ratio <= 0.333:
        return "OPEN_RECTANGLE"

    rectangle_filled_waiting_matches = compare_images(
        image, RECTANGLE_FILLED_WAITING_IMAGE
    )
    if rectangle_filled_waiting_matches >= 15 and black_to_white_ratio >= 5:
        return "RECTANGLE_FILLED_WAITING"

    rectangle_filled_full_checkmark_matches = compare_images(
        image, RECTANGLE_FILLED_FULL_CHECKMARK_IMAGE
    )
    if rectangle_filled_full_checkmark_matches >= 15 and black_to_white_ratio >= 5:
        return "RECTANGLE_FILLED_FULL_CHECKMARK"

    rectangle_filled_half_checkmark_matches = compare_images(
        image, FILLED_RECTANGLE_HALF_CHECKMARK_IMAGE
    )
    if rectangle_filled_half_checkmark_matches >= 15 and black_to_white_ratio >= 5:
        return "RECTANGLE_FILLED_HALF_CHECKMARK"

    if rectangle_filled_waiting_matches >= 15 and black_to_white_ratio >= 0.333:
        return "RECTANGLE_PARTIALLY_FILLED"

    if black_to_white_ratio >= 0.333 and (
        open_rectangle_matches >= 6
        or rectangle_filled_waiting_matches >= 6
        or rectangle_filled_full_checkmark_matches >= 6
        or rectangle_filled_half_checkmark_matches >= 6
    ):
        return "RECTANGLE_PARTIALLY_FILLED"

    if open_rectangle_matches >= 6:
        return "UNKNOWN_RECTANGLE"

    return "UNKNOWN"


def walmart_captcha_required(driver: WebDriver):
    # https://www.walmart.com/blocked

    if "www.walmart.com/blocked" in driver.current_url.lower():
        return True

    result = take_screenshot_and_get_walmart_captcha_cropped_rectangle(driver)
    cropped_screenshot_image = result["image"]
    internal_status = get_walmart_captcha_internal_status(cropped_screenshot_image)
    if internal_status not in ["UNKNOWN", "UNKNOWN_RECTANGLE"]:
        return True

    return False


def solve_walmart_captcha(driver: WebDriver):
    # https://www.walmart.com/blocked

    try:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    except:
        pass

    time.sleep(3)

    attempts = 0
    while attempts < 1:
        try:
            attempts += 1

            if walmart_captcha_required(driver):
                print("Walmart CAPTCHA found. Attempting to solve...")
                solve_walmart_captcha_recursive(driver)
                time.sleep(3)
                try:
                    driver.execute_script(
                        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                    )
                except:
                    pass
        except:
            traceback.print_exc()
            print("Likely no more Walmart CAPTCHA")
            break


def take_screenshot_and_get_walmart_captcha_cropped_rectangle(driver: WebDriver):
    screenshot_image_bytes = driver.get_screenshot_as_png()
    image_array = np.frombuffer(screenshot_image_bytes, dtype=np.uint8)
    screenshot_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    result = get_walmart_captcha_cropped_rectangle_from_screenshot(screenshot_image)
    return result


def get_walmart_captcha_cropped_rectangle_from_screenshot(screenshot_image):
    # Convert to grayscale
    gray = cv2.cvtColor(screenshot_image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use adaptive thresholding or simple thresholding
    _, binary = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)

    # Edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize variables to track the largest rectangle
    max_area = 0
    largest_rect = None

    for contour in contours:
        # Approximate the contour
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)

        # Check if the contour has more than 4 corners (indicating a rounded rectangle)
        if len(approx) > 4:
            # Get the bounding rectangle of the contour
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h

            aspect_ratio = w / h
            if 1.777 < aspect_ratio < 2.777:

                # look for a specific area
                if 18000 < area < 70000:
                    cropped_image = screenshot_image[y : y + h, x : x + w]

                    # make sure the rectangle is close to the one we're looking for
                    internal_status = get_walmart_captcha_internal_status(cropped_image)
                    if internal_status not in ["UNKNOWN", "UNKNOWN_RECTANGLE"]:
                        # Update the largest rectangle if the current one is bigger
                        if area > max_area:
                            max_area = area
                            largest_rect = (x, y, w, h)

    # Crop and display the largest rectangle if found
    if largest_rect is not None:
        x, y, w, h = largest_rect
        cropped_image = screenshot_image[y : y + h, x : x + w]

        # Show the cropped image
        print(f"Largest rectangle area: {w * h}")
        print(f"Largest rectangle aspect ratio: {w / h}")

        # leaving the following comment block for debug purposes when needed -- TODO: add argparse arg to toggle
        # cv2.imshow("Largest Rectangle", cropped_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        screenshot_height, screenshot_width, screenshot_channels = (
            screenshot_image.shape
        )
        return {
            "image": cropped_image,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "screenshot_width": screenshot_width,
            "screenshot_height": screenshot_height,
        }
    else:
        print("No valid rectangles detected.")

    return {
        "image": None,
        "x": 0,
        "y": 0,
        "width": 0,
        "height": 0,
        "screenshot_width": 0,
        "screenshot_height": 0,
    }


def solve_walmart_captcha_recursive(
    driver: WebDriver, retry=20, unknown_status_count=0
):
    driver.maximize_window()
    driver.switch_to.default_content()

    try:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    except:
        pass

    if retry <= 0:
        return False

    # do not click element if not an open rectangle
    result = take_screenshot_and_get_walmart_captcha_cropped_rectangle(driver)
    cropped_screenshot_image = result["image"]
    internal_status = get_walmart_captcha_internal_status(cropped_screenshot_image)
    if internal_status != "OPEN_RECTANGLE":
        if internal_status in ["UNKNOWN", "UNKNOWN_RECTANGLE"]:
            unknown_status_count += 1

            if unknown_status_count >= 5:
                print(
                    "Unknown status 5 times in a row. Likely CAPTCHA solved. Exiting loop..."
                )
                return

        # randomly click if filled since the wait loop is long sometimes and it seems like they want you to click anyway
        if random.randint(0, 5) == 3:
            html_elem = driver.find_element(By.TAG_NAME, "body")

            print("Randomly clicking filled rectangle...")
            x = int(result["x"] + result["width"] // 2)

            # subtract half of screenshot width since Selenium bases offsets off center point of in-view element
            x -= int(result["screenshot_width"] // 2)

            # add some randomness
            x += random.randint(int(-0.3 * result["width"]), int(0.3 * result["width"]))

            y = int(result["y"] + result["height"] // 2)

            # subtract half of screenshot width since Selenium bases offsets off center point of in-view element
            y -= int(result["screenshot_height"] // 2)

            # add some randomness
            y += random.randint(
                int(-0.3 * result["height"]), int(0.3 * result["height"])
            )

            print(f"Randomly moving mouse by offset from center of page {x}, {y}...")
            actions = ActionChains(driver)
            actions.move_to_element_with_offset(html_elem, x, y)
            actions.click(None)
            actions.perform()
            time.sleep(0.1)

        print(
            "No open rectangle detected. Not going to click element. Waiting 5 seconds then retrying..."
        )
        time.sleep(5)
        return solve_walmart_captcha_recursive(driver, retry, unknown_status_count)

    print("Clicking and holding element...")

    # ActionChains(driver).click_and_hold(element).perform()
    html_elem = driver.find_element(By.TAG_NAME, "body")

    x = int(result["x"] + result["width"] // 2)

    # subtract half of screenshot width since Selenium bases offsets off center point of in-view element
    x -= int(result["screenshot_width"] // 2)

    # add some randomness
    x += random.randint(int(-0.3 * result["width"]), int(0.3 * result["width"]))

    y = int(result["y"] + result["height"] // 2)

    # subtract half of screenshot width since Selenium bases offsets off center point of in-view element
    y -= int(result["screenshot_height"] // 2)

    # add some randomness
    y += random.randint(int(-0.3 * result["height"]), int(0.3 * result["height"]))

    print(f"Moving mouse by offset from center of page {x}, {y} then clicking...")

    actions = ActionChains(driver)
    actions.move_to_element_with_offset(html_elem, x, y)
    actions.click_and_hold(None)
    actions.perform()

    time.sleep(2)

    start_time = time.time()

    while True:
        driver.maximize_window()
        driver.switch_to.default_content()

        if time.time() - start_time > 20:
            print("Already waited 20 seconds, exiting loop...")
            print("Releasing button...")
            ActionChains(driver).release(None).perform()
            break

        try:
            # randomly move mouse every so often
            if random.randint(0, 100) == 50:
                x = int(result["x"] + result["width"] // 2)

                # subtract half of screenshot width since Selenium bases offsets off center point of in-view element
                x -= int(result["screenshot_width"] // 2)

                # add some randomness
                x += random.randint(
                    int(-0.3 * result["width"]), int(0.3 * result["width"])
                )

                y = int(result["y"] + result["height"] // 2)

                # subtract half of screenshot width since Selenium bases offsets off center point of in-view element
                y -= int(result["screenshot_height"] // 2)

                # add some randomness
                y += random.randint(
                    int(-0.3 * result["height"]), int(0.3 * result["height"])
                )

                print(
                    f"Randomly moving mouse by offset from center of page {x}, {y}..."
                )
                actions = ActionChains(driver)
                actions.move_to_element_with_offset(html_elem, x, y)
                actions.perform()
                time.sleep(0.1)

            result = take_screenshot_and_get_walmart_captcha_cropped_rectangle(driver)
            cropped_screenshot_image = result["image"]
            status = get_walmart_captcha_status(cropped_screenshot_image)
            print(f"status: {status}")

            if status == "COMPLETE":
                print("Releasing button...")
                ActionChains(driver).release(None).perform()
                print("Waiting 3 seconds...")
                time.sleep(3)
                print("Retrying to see if there is a new CAPTCHA")
                return solve_walmart_captcha_recursive(
                    driver, retry - 1, unknown_status_count
                )
            elif status == "NOT_STARTED":
                print("Not started, so retrying...")
                return solve_walmart_captcha_recursive(
                    driver, retry - 1, unknown_status_count
                )
            elif status == "IN_PROGRESS":
                print("In progress, so taking no action")
            elif status == "UNKNOWN":
                unknown_status_count += 1

                if unknown_status_count >= 5:
                    print(
                        "Unknown status 5 times in a row. Likely CAPTCHA solved. Exiting loop..."
                    )
                    return

                print("Unknown status, so waiting a few seconds then retrying...")
                time.sleep(3)
                return solve_walmart_captcha_recursive(
                    driver, retry - 1, unknown_status_count
                )
        except:
            traceback.print_exc()

        time.sleep(0.1)

    time.sleep(1)
    return solve_walmart_captcha_recursive(driver, retry - 1, unknown_status_count)
