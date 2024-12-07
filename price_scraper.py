# pip install amazoncaptcha requests selenium stealthenium opencv-python numpy

# no longer needed: tls-client pytz

import cv2
from datetime import datetime
from io import BytesIO
import numpy as np
import pathlib
from PIL import Image
from pprint import pprint
import os
import random
import subprocess
import sqlite3
import time
import traceback
import typing

from amazoncaptcha import AmazonCaptcha
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from stealthenium import stealth


products = [
    # Phones
    {
        "name": "Samsung Galaxy S24 128GB",
        "url": "https://www.amazon.com/SAMSUNG-Smartphone-Unlocked-Processor-SM-S921UZKAXAA/dp/B0CMDRCZBJ?crid=3TGR10222RZQ5&dib=eyJ2IjoiMSJ9.y9JFwPsCZ9T11Z3y5qhMBtRMll8jhQlxP_N-PHhBkFEwkZRpqsxsXsELKj5t4TZ4RDCDPFvsPDINtShkeCC55KHdCxqCaT1_yA7y1JA3Kv47g6u30i2wWq7zyCS70hdxLRKth2JwtbIINpHORPqqe57O8WVTk9dokRXvmEBgdhXHuknB8TgPLhjv19BPN8C7S5mHXupTmfIju5up-RSTHdnHKduTNuzkhgUKGA3yhMQ.ZweycM1UvriqOnzi2ruEPCOdOh0nSx2x1MNMr4zFeRU&dib_tag=se&keywords=galaxy+s24&qid=1732848837&sprefix=galaxy+s24%2Caps%2C132&sr=8-3",
        "target_price": 400,
    },

    {
        "name": "Samsung Galaxy S24 128GB",
        "url": "https://www.bestbuy.com/site/samsung-galaxy-s24-128gb-unlocked-onyx-black/6569840.p?skuId=6569840",
        "target_price": 400,
    },

    {
        "name": "Samsung Galaxy S24 128GB",
        "url": "https://www.walmart.com/ip/SAMSUNG-Galaxy-S24-Cell-Phone-128GB-AI-Smartphone-Unlocked-Android-50MP-Camera-Fastest-Processor-Long-Battery-Life-US-Version-2024-Onyx-Black/5400713211?classType=REGULAR&from=/search",
        "target_price": 400,
    },

    {
        "name": "Samsung Galaxy S24 128GB",
        "url": "https://www.samsung.com/us/smartphones/galaxy-s24/buy/galaxy-s24-128gb-unlocked-sm-s921ulbaxaa/",
        "target_price": 400,
    },


    # Mowers
    {
        "name": 'Hart 20" Push Mower (not self-propelled)',
        "url": "https://www.walmart.com/ip/HART-40-Volt-20-inch-Cordless-Brushless-Push-Mower-Kit-1-6-0Ah-Lithium-Ion-Battery/990402225?classType=VARIANT&from=/search",
        "target_price": 250,
    },

    {
        "name": 'Hart 20" Push Mower (self-propelled)',
        "url": "https://www.walmart.com/ip/HART-40-Volt-20-inch-Self-Propelled-Battery-Powered-Brushless-Mower-Kit-1-6-0Ah-Lithium-Ion-Battery/399430920?classType=VARIANT&athbdg=L1600&from=/search",
        "target_price": 300,
    },

    {
        "name": 'Hart 20" Push Mower (not self-propelled)',
        "url": "https://harttools.com/products/40v-20-push-mower-kit",
        "target_price": 250,
    },

    {
        "name": 'Hart 20" Push Mower (self-propelled)',
        "url": "https://harttools.com/products/40v-brushless-20-self-propelled-mower",
        "target_price": 300,
    },


    # # Home products
    {
        "name": 'Hugger 56 in. LED Espresso Bronze Ceiling Fan',
        "url": "https://www.homedepot.com/p/Hugger-56-in-LED-Espresso-Bronze-Ceiling-Fan-AL383D-EB/304542818",
        "target_price": 46,
    },

    {
        "name": 'Hugger 52 in. LED Gunmetal Ceiling Fan',
        "url": "https://www.homedepot.com/p/Hugger-52-in-LED-Gunmetal-Ceiling-Fan-AL383LED-GM/304542817",
        "target_price": 45,
    },

    {
        "name": 'Trice 52 in. LED Espresso Bronze Ceiling Fan',
        "url": "https://www.homedepot.com/p/Trice-52-in-LED-Espresso-Bronze-Ceiling-Fan-YG269BP-EB/304542645?MERCH=REC-_-brand_based_collection-_-304542817-_-4-_-n/a-_-n/a-_-n/a-_-n/a-_-n/a",
        "target_price": 45,
    },
]


def create_tables(cursor: sqlite3.Cursor):
    sql = """
    --begin-sql
        CREATE TABLE IF NOT EXISTS pricelog (
            product_name TEXT,
            store TEXT,
            url TEXT,
            target_price DECIMAL,
            current_price DECIMAL,
            status TEXT,
            info TEXT,
            timestamp_added TIMESTAMP
        )
    --end-sql
    """

    cursor.execute(sql)


def add_pricelog_record(cursor: sqlite3.Cursor, product_name: str, store: str, url: str, target_price: float, current_price: float, status: str, info: str):
    sql = """
    --begin-sql
        INSERT INTO pricelog
        (product_name, store, url, target_price, current_price, status, info, timestamp_added)
        VALUES
        (?, ?, ?, ?, ?, ?, ?, datetime(current_timestamp, 'localtime'))
    --end-sql
    """

    cursor.execute(sql, (
        product_name,
        store,
        url,
        target_price,
        current_price,
        status,
        info,
    ))


def click_samsung_no_trade_in_button(driver: WebDriver):
    try:
        no_trade_in_button_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".TradeInOption_tradein__wrapper__Bmb3w:has(.TradeInOption_no_tradein__label__D39Ic)"))
        )

        ActionChains(driver).scroll_to_element(no_trade_in_button_elem).perform()

        no_trade_in_button_elem.click()
        print("Clicked Samsung no trade in button")
        time.sleep(2)
    except:
        traceback.print_exc()
        print("No Samsung trade in button selection")


def get_price(driver: WebDriver, product_dict: dict) -> dict:
    price = -1
    error = False
    info = "OK"

    if "amazon.com" in product_dict["url"]:
        store = "Amazon"
        css_selector = "#newAccordionRow_0 #corePrice_feature_div span.a-offscreen"
    elif "bestbuy.com" in product_dict["url"]:
        store = "Best Buy"
        css_selector = ".priceView-layout-large .priceView-customer-price > span[aria-hidden='true']"
    elif "walmart.com" in product_dict["url"]:
        store = "Walmart"
        css_selector = ".buy-box-container span[itemprop='price'"
    elif "harttools.com" in product_dict["url"]:
        store = "Hart Tools"
        css_selector = ".false.mb-0"
    elif "samsung.com" in product_dict["url"]:
        # note: this currently just scrapes the default first tab selected
        store = "Samsung"
        css_selector = ".DeviceTile_selected__H71O3 .DeviceTile_device__price___rO94"
    elif "homedepot.com" in product_dict["url"]:
        store = "Home Depot"

        # Home Depot splits the price to 2 span elements. 1 has high order amount and other has low order amount.
        # Custom handling of this is done below
        css_selector = ""
    else:
        store = "Unknown"
        css_selector = ""
        error = True
        info = f"website not supported: {product_dict['url']}"
        print(info)

    print(f"Scraping store {store} - product {product_dict['name']}...")

    # navigate to URL
    if not error:
        try:
            driver.maximize_window()
            driver.get(product_dict["url"])
            time.sleep(2)
        except:
            error = True
            info = "exception"
            traceback.print_exc()

    # scrape price
    if not error:
        if "amazon.com" in product_dict["url"]:
            captcha_required = False
            try:
                captcha_required = WebDriverWait(driver, 10).until(amazon_captcha_required)
            except:
                traceback.print_exc()

            if captcha_required:
                print("Amazon CAPTCHA required")
                solve_amazon_captcha(driver)
            else:
                print("No Amazon CAPTCHA required")

        if "walmart.com" in product_dict["url"]:
            captcha_required = False
            try:
                captcha_required = WebDriverWait(driver, 10).until(walmart_captcha_required)
            except:
                traceback.print_exc()

            if captcha_required:
                print("Walmart CAPTCHA required")
                solve_walmart_captcha(driver)
            else:
                print("No Walmart CAPTCHA required")

        # need to click the no trade in button on samsung.com for phones
        if "samsung.com" in product_dict["url"]:
            click_samsung_no_trade_in_button(driver)

        # generic handler to get price by CSS selector
        try:
            if "homedepot.com" in product_dict["url"]:
                price_high_order_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".sui-text-9xl.sui--translate-y-\\[0\\.5rem\\]"))
                )

                price_high_order = price_high_order_element.get_attribute("textContent")

                price_low_order_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".sui-sr-only + .sui-text-3xl"))
                )

                price_low_order = price_low_order_element.get_attribute("textContent")

                if price_high_order and price_low_order:
                    price = f"${price_high_order.strip()}.{price_low_order.strip()}"
            else:
                price_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
                )

                price = price_element.get_attribute("textContent")

            if price:
                price = price.lower().strip()
                price = price.replace("$", "")
                price = price.replace("now", "") # remove Now prefix from Walmart element that sometimes exists
                price = price.strip()
                if price:
                    price = float(price)
                    print(f"Found price: {price}")
            
            if not price:
                error = True
                info = "price not found"
                print(info)
        except:
            error = True
            info = "exception"
            traceback.print_exc()
    
    return {
        "name": product_dict["name"],
        "url": product_dict["url"],
        "store": store,
        "current_price": price,
        "target_price": product_dict["target_price"],
        "error": error,
        "info": info,
    }


def record_and_output_results(cursor: sqlite3.Cursor, results: typing.List['dict']):
    print("Current prices:")
    for result_dict in results:
        print(f"[{result_dict['store']}] {result_dict['name']}: {result_dict['current_price']}")

        if not result_dict["error"]:
            if result_dict["current_price"] < result_dict["target_price"]:
                status = "BELOW_TARGET"
            elif result_dict["current_price"] == result_dict["target_price"]:
                status = "AT_TARGET"
            else:
                status = "ABOVE_TARGET"
        else:
            status = "ERROR"

        add_pricelog_record(cursor, result_dict['name'], result_dict['store'], result_dict['url'], result_dict['target_price'], result_dict['current_price'], status, result_dict["info"])


def should_send_target_live_notification(cursor: sqlite3.Cursor, product_name: str, store: str):
    # return 1 if there are at least 2 target price live records of the product and store that have
    # been recorded in the last day
    sql = """
    --begin-sql
        SELECT 1
        FROM pricelog
        WHERE product_name = ?
            AND store = ?
            AND current_price <= target_price
            AND status != 'ERROR'
            AND timestamp_added BETWEEN datetime(current_timestamp, '-1 days', 'localtime') AND datetime(current_timestamp, 'localtime')
        GROUP BY product_name
        HAVING count(*) > 1
        LIMIT 1
    --end-sql
    """
    cursor.execute(sql, (
        product_name,
        store,
    ))

    result = cursor.fetchone()
    if result and len(result) > 0 and result[0] == 1:
        return False

    return True


def should_send_error_notification(cursor: sqlite3.Cursor, product_name: str, store: str):
    # this function should only be called if there is a current error condition on the product

    # return 1 if there has been at least 1 successful price record of the product in
    # the last 24 hours
    sql = """
    --begin-sql
        SELECT 1
        FROM pricelog
        WHERE product_name = ?
            AND store = ?
            AND status != 'ERROR'
            AND timestamp_added BETWEEN datetime(current_timestamp, '-24 hours', 'localtime') AND datetime(current_timestamp, 'localtime')
        GROUP BY product_name
        HAVING count(*) > 1
        LIMIT 1
    --end-sql
    """
    cursor.execute(sql, (
        product_name,
        store,
    ))

    result = cursor.fetchone()
    if result and len(result) > 0 and result[0] == 1:
        return False

    return True


def notify_when_below_target(cursor: sqlite3.Cursor, results: typing.List['dict']):
    for result_dict in results:
        message = ""
        if not result_dict["error"]:
            if result_dict["current_price"] <= result_dict["target_price"]:
                if should_send_target_live_notification(cursor, result_dict['name'], result_dict['store']):
                    message = f"Target price is live: [{result_dict['store']}] {result_dict['name']}: {result_dict['current_price']}"
        else:
            if should_send_error_notification(cursor, result_dict['name'], result_dict['store']):
                message = f"Error getting price: [{result_dict['store']}] {result_dict['name']}: {result_dict['info']}"

        if message:
            print(message)
            response = requests.post("https://ntfy.sh/dkornacki_price_tracker", data=message)
            if response.status_code == 200:
                print("Successfully sent ntfy notificaiton")


def amazon_captcha_required(driver: WebDriver):
    # https://www.amazon.com/errors/validateCaptcha

    if "/validatecaptcha" in driver.current_url.lower():
        return True

    CAPTCHA_TEXT_TO_SEARCH = "type the characters you see in this image"

    headers = driver.find_elements(By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6")
    found = any(CAPTCHA_TEXT_TO_SEARCH in header.text.lower() for header in headers)
    if not found:
        found = any(CAPTCHA_TEXT_TO_SEARCH in header.get_attribute("textContent").lower() for header in headers)

    return found


def solve_amazon_captcha(driver: WebDriver):
    #driver.maximize_window()
    #driver.get("https://www.amazon.com/errors/validateCaptcha")

    img_elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".a-box img"))
    )
    img_src = img_elem.get_attribute("src")

    print("Solving...")
    captcha = AmazonCaptcha.fromlink(img_src)
    solution = captcha.solve()

    if solution and solution.lower() != 'not solved':
        print(f"Captcha solved: {solution}")
        time.sleep(5)
        input_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#captchacharacters"))
        )
        input_elem.send_keys(solution)
        time.sleep(1)
        input_elem.send_keys(Keys.ENTER)
    else:
        raise Exception("Could not solve CAPTCHA")


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


open_rectangle_image = cv2.imread(r"\\server2\General\Archive\Scripts\walmart_captcha_images\open_rectangle.png")
rectangle_filled_waiting_image = cv2.imread(r"\\server2\General\Archive\Scripts\walmart_captcha_images\rectangle_filled_waiting.png")
rectangle_filled_full_checkmark_image = cv2.imread(r"\\server2\General\Archive\Scripts\walmart_captcha_images\rectangle_filled_full_checkmark.png")
filled_rectangle_half_checkmark_image = cv2.imread(r"\\server2\General\Archive\Scripts\walmart_captcha_images\filled_rectangle_half_checkmark.png")


def get_walmart_captcha_internal_status(image):
    if image is None:
        return "UNKNOWN"

    black_to_white_ratio = get_black_to_white_ratio(image)
    print(f"black_to_white_ratio: {black_to_white_ratio}")

    open_rectangle_matches = compare_images(image, open_rectangle_image)
    if open_rectangle_matches >= 70 and black_to_white_ratio <= 0.333:
        return "OPEN_RECTANGLE"
    
    rectangle_filled_waiting_matches = compare_images(image, rectangle_filled_waiting_image)
    if rectangle_filled_waiting_matches >= 15 and black_to_white_ratio >= 5:
        return "RECTANGLE_FILLED_WAITING"

    rectangle_filled_full_checkmark_matches = compare_images(image, rectangle_filled_full_checkmark_image)
    if rectangle_filled_full_checkmark_matches >= 15 and black_to_white_ratio >= 5:
        return "RECTANGLE_FILLED_FULL_CHECKMARK"
    
    rectangle_filled_half_checkmark_matches = compare_images(image, filled_rectangle_half_checkmark_image)
    if rectangle_filled_half_checkmark_matches >= 15 and black_to_white_ratio >= 5:
        return "RECTANGLE_FILLED_HALF_CHECKMARK"

    if rectangle_filled_waiting_matches >= 15 and black_to_white_ratio >= 0.333:
        return "RECTANGLE_PARTIALLY_FILLED"

    if (black_to_white_ratio >= 0.333 and (
            open_rectangle_matches >= 6
            or rectangle_filled_waiting_matches >= 6
            or rectangle_filled_full_checkmark_matches >= 6
            or rectangle_filled_half_checkmark_matches >= 6)):
        return "RECTANGLE_PARTIALLY_FILLED"

    if open_rectangle_matches >= 6:
        return "UNKNOWN_RECTANGLE"

    return "UNKNOWN"


def get_black_to_white_ratio(image):
    if image is None:
        return 0

    # Define thresholds
    # Black/gray: pixel values from 0 to 200 (adjust threshold as needed)
    # White: pixel values from 201 to 255
    black_gray_mask = (image <= 200)
    white_mask = (image > 200)

    # Count pixels
    black_gray_count = np.sum(black_gray_mask)
    white_count = np.sum(white_mask)

    # Calculate the ratio
    if white_count > 0:  # Avoid division by zero
        ratio = black_gray_count / white_count
    else:
        ratio = float('inf')  # All pixels are black/gray
    
    return ratio


def walmart_captcha_required(driver: WebDriver):
    # https://www.walmart.com/blocked

    if "www.walmart.com/blocked" in driver.current_url.lower():
        return True

    # try:
    #     element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID,'px-captcha')))
    #     if element:
    #         return True
    # except:
    #     pass

    result = take_screenshot_and_get_walmart_captcha_cropped_rectangle(driver)
    cropped_screenshot_image = result["image"]
    internal_status = get_walmart_captcha_internal_status(cropped_screenshot_image)
    if internal_status not in ["UNKNOWN", "UNKNOWN_RECTANGLE"]:
        return True
    
    return False


def solve_walmart_captcha(driver: WebDriver):
    #driver.maximize_window()
    #driver.get("https://www.walmart.com/blocked")

    time.sleep(3)
    #subprocess.run(['python', r'\\server2\General\Archive\Scripts\external_packages\perimeterx_solution_walmart_branch\solve.py'], cwd=r'\\server2\General\Archive\Scripts\external_packages\perimeterx_solution_walmart_branch')
    
    attempts = 0
    while attempts < 1:
        try:
            attempts += 1
            # element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID,'px-captcha')))
            # if element:
            if walmart_captcha_required(driver):
                print("Walmart CAPTCHA found. Attempting to solve...")
                solve_walmart_captcha_recursive(driver)
        except:
            traceback.print_exc()
            print("Likely no more Walmart CAPTCHA")
            break


def take_screenshot_and_get_walmart_captcha_cropped_rectangle(driver: WebDriver):
    screenshot_image_bytes = driver.get_screenshot_as_png() 
    image_array = np.frombuffer(screenshot_image_bytes, dtype=np.uint8)
    screenshot_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    #cv2.imwrite(f"screenshots/screenshot_{datetime.now().isoformat().replace(':', '').replace(' ', '_').replace('.', '_')}.png", screenshot_image)
    result = get_walmart_captcha_cropped_rectangle_from_screenshot(screenshot_image)
    #if result["image"] is not None:
    #    cv2.imwrite(f"screenshots/crop_{datetime.now().isoformat().replace(':', '').replace(' ', '_').replace('.', '_')}.png", result["image"])

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
                    print(area)
                    cropped_image = screenshot_image[y:y+h, x:x+w]

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
        cropped_image = screenshot_image[y:y+h, x:x+w]
        
        # Show the cropped image
        print(f"Largest rectangle area: {w * h}")
        print(f"Largest rectangle aspect ratio: {w / h}")
        # cv2.imshow("Largest Rectangle", cropped_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        screenshot_height, screenshot_width, screenshot_channels = screenshot_image.shape
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


def compare_images(image1, image2):
    if image1 is None or image2 is None:
        return 0

    # Load the images
    # image1 = cv2.imread('image1.jpg')
    # image2 = cv2.imread('image2.jpg')

    # Convert to grayscale
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Detect ORB keypoints and descriptors
    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(gray2, None)

    # Match descriptors using BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)

    # Sort matches by distance
    matches = sorted(matches, key=lambda x: x.distance)

    # Check the number of good matches
    print(f"Number of matches: {len(matches)}")
    # if len(matches) > 10:  # Threshold for similarity
    #     print("Images are similar")
    #     cv2.imshow(f"{len(matches)} Images are similar - Image 1", image1)
    #     cv2.imshow(f"{len(matches)} Images are similar - Image 2", image2)
    # else:
    #     print("Images are not similar")
    #     cv2.imshow(f"{len(matches)} Images are not similar - Image 1", image1)
    #     cv2.imshow(f"{len(matches)} Images are not similar - Image 2", image2)

    # # Wait for a key press and close the windows
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return len(matches)


def solve_walmart_captcha_recursive(driver: WebDriver, retry=20, unknown_status_count=0):
    driver.maximize_window()
    driver.switch_to.default_content()

    if retry <= 0:
        return False

    # element = None
    # try:
    #     element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#px-captcha")))
    #     time.sleep(0.5)
    # except:
    #     traceback.print_exc()
    #     print("Did not find CAPTCHA element")
    #     return

    # if  element:

    # do not click element if not an open rectangle
    result = take_screenshot_and_get_walmart_captcha_cropped_rectangle(driver)
    cropped_screenshot_image = result["image"]
    internal_status = get_walmart_captcha_internal_status(cropped_screenshot_image)
    if internal_status != "OPEN_RECTANGLE":
        if internal_status in ["UNKNOWN", "UNKNOWN_RECTANGLE"]:
            unknown_status_count += 1

            if unknown_status_count >= 5:
                print("Unknown status 5 times in a row. Likely CAPTCHA solved. Exiting loop...")
                return

        # randomly click if filled since the wait loop is long sometimes and it seems like they want you to click anyway
        if random.randint(0, 5) == 3:
            html_elem = driver.find_element(By.TAG_NAME, 'body')

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
            y += random.randint(int(-0.3 * result["height"]), int(0.3 * result["height"]))

            print(f"Randomly moving mouse by offset from center of page {x}, {y}...")
            actions = ActionChains(driver)
            actions.move_to_element_with_offset(html_elem, x, y)
            actions.click(None)
            actions.perform()
            time.sleep(0.1)

        print("No open rectangle detected. Not going to click element. Waiting 5 seconds then retrying...")
        time.sleep(5)
        return solve_walmart_captcha_recursive(driver, retry, unknown_status_count)


    print("Clicking and holding element...")

    #ActionChains(driver).click_and_hold(element).perform()
    html_elem = driver.find_element(By.TAG_NAME, 'body')

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
                x += random.randint(int(-0.3 * result["width"]), int(0.3 * result["width"]))

                y = int(result["y"] + result["height"] // 2)

                # subtract half of screenshot width since Selenium bases offsets off center point of in-view element
                y -= int(result["screenshot_height"] // 2)

                # add some randomness
                y += random.randint(int(-0.3 * result["height"]), int(0.3 * result["height"]))

                print(f"Randomly moving mouse by offset from center of page {x}, {y}...")
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
                return solve_walmart_captcha_recursive(driver, retry - 1, unknown_status_count)
            elif status == "NOT_STARTED":
                print("Not started, so retrying...")
                return solve_walmart_captcha_recursive(driver, retry - 1, unknown_status_count)
            elif status == "IN_PROGRESS":
                print("In progress, so taking no action")
            elif status == "UNKNOWN":
                unknown_status_count += 1

                if unknown_status_count >= 5:
                    print("Unknown status 5 times in a row. Likely CAPTCHA solved. Exiting loop...")
                    return

                print("Unknown status, so waiting a few seconds then retrying...")
                time.sleep(3)
                return solve_walmart_captcha_recursive(driver, retry - 1, unknown_status_count)
        except:
            traceback.print_exc()

        time.sleep(0.1)

    time.sleep(1)
    return solve_walmart_captcha_recursive(driver, retry - 1, unknown_status_count)


def get_new_driver() -> WebDriver:
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # headless does not work for BestBuy
    #options.add_argument("--headless=new")

    # to keep browser open for testing (also comment driver.quit() at end of script)
    #options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options, service=webdriver.ChromeService(port=4444))
    driver.command_executor._url = "http://localhost:4444"

    # bypass bot detection (fixed Home Depot scraping)
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    print(f"Driver user agent: {driver.execute_script('return navigator.userAgent')}")
    return driver


def main():
    # pathlib.Path("screenshots/").mkdir(parents=True, exist_ok=True)

    # image_paths = [
    #     'screenshot_2024-12-07T101130_153283.png',
    # #     r"\\server2\General\Archive\Scripts\walmart_captcha_images\open_rectangle.png",
    # #     r"\\server2\General\Archive\Scripts\walmart_captcha_images\rectangle_filled_waiting.png",
    # #     r"\\server2\General\Archive\Scripts\walmart_captcha_images\rectangle_filled_full_checkmark.png",
    # #     r"\\server2\General\Archive\Scripts\walmart_captcha_images\filled_rectangle_half_checkmark.png",
    # #     # 'screenshot_open_rectangle.png',
    # #     # 'screenshot_rectangle_partially_filled.png',
    # #     # 'screenshot_filled_rectangle_half_checkmark.png',
    # #     # 'screenshot_rectangle_filled_full_checkmark.png',
    # #     # 'screenshot_rectangle_filled_waiting.png',
    # ]

    # for image_path in image_paths:
    #     print(image_path)
    #     screenshot_image = cv2.imread(image_path)
    #     #print(get_walmart_captcha_status(screenshot_image))

    #     cropped_screenshot_image = None
    #     result = get_walmart_captcha_cropped_rectangle_from_screenshot(screenshot_image)
    #     if result and result["image"] is not None:
    #        cropped_screenshot_image = result["image"]

    #     print(get_walmart_captcha_status(cropped_screenshot_image))
       
    # return

    while True:
        try:
            with sqlite3.connect("price_scraper.db", isolation_level=None) as conn:
                cursor = conn.cursor()

                create_tables(cursor)

                

                # driver = get_new_driver()
                # driver.maximize_window()
                # driver.get("https://www.walmart.com/blocked")
                # time.sleep(3)
                # solve_walmart_captcha(driver)
                # driver.quit()
                # return



                results = []
                for product_dict in products:
                    try:
                        print("Getting new driver...")
                        driver = get_new_driver()

                        # add additional wait time for Walmart
                        # if "walmart.com" in product_dict["url"]:
                        #     print("Current product is at Walmart. Waiting an additional 60 seconds before loading page...")
                        #     time.sleep(62)
                        
                        result = get_price(driver, product_dict)
                        if result:
                            results.append(result)

                        # even if price is retrieved on Walmart now, sometimes the CAPTCHA shows up to 10 seconds after page load
                        # just check and solve if so
                        if result["current_price"] != -1:
                            print("Even though found price, checking Walmart CAPTCHA again...")
                            if "walmart.com" in product_dict["url"]:
                                captcha_required = False
                                try:
                                    captcha_required = WebDriverWait(driver, 10).until(walmart_captcha_required)
                                except:
                                    traceback.print_exc()

                                if captcha_required:
                                    print("Walmart CAPTCHA required")
                                    solve_walmart_captcha(driver)
                                else:
                                    print("No Walmart CAPTCHA required")
                    except:
                        traceback.print_exc()
                    finally:
                        time.sleep(2)
                        print("Quitting driver...")
                        driver.quit()

                    print("Waiting 60 seconds...")
                    time.sleep(60)

                record_and_output_results(cursor, results)
                notify_when_below_target(cursor, results)
        except:
            traceback.print_exc()

        # wait about an hour
        print("Waiting about 1 hour...")
        time.sleep(3600 + 120)


if __name__ == '__main__':
    main()
