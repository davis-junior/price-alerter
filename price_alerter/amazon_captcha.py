import time

from amazoncaptcha import AmazonCaptcha
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def amazon_captcha_required(driver: WebDriver):
    # https://www.amazon.com/errors/validateCaptcha

    if "/validatecaptcha" in driver.current_url.lower():
        return True

    CAPTCHA_TEXT_TO_SEARCH = "type the characters you see in this image"

    headers = driver.find_elements(By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6")
    found = any(CAPTCHA_TEXT_TO_SEARCH in header.text.lower() for header in headers)
    if not found:
        found = any(
            CAPTCHA_TEXT_TO_SEARCH in header.get_attribute("textContent").lower()
            for header in headers
        )

    return found


def solve_amazon_captcha(driver: WebDriver):
    # https://www.amazon.com/errors/validateCaptcha

    try:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    except:
        pass

    img_elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".a-box img"))
    )
    img_src = img_elem.get_attribute("src")

    print("Solving...")
    captcha = AmazonCaptcha.fromlink(img_src)
    solution = captcha.solve()

    if solution and solution.lower() != "not solved":
        print(f"Captcha solved: {solution}")
        time.sleep(5)
        input_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#captchacharacters"))
        )
        input_elem.send_keys(solution)
        time.sleep(1)
        input_elem.send_keys(Keys.ENTER)

        time.sleep(3)
        try:
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
        except:
            pass
    else:
        raise Exception("Could not solve CAPTCHA")
