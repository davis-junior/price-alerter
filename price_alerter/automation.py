import time
import traceback

from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def click_samsung_no_trade_in_button(driver: WebDriver):
    try:
        no_trade_in_button_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    ".TradeInOption_tradein__wrapper__Bmb3w:has(.TradeInOption_no_tradein__label__D39Ic)",
                )
            )
        )

        ActionChains(driver).scroll_to_element(no_trade_in_button_elem).perform()

        no_trade_in_button_elem.click()
        print("Clicked Samsung no trade in button")
        time.sleep(2)
    except:
        traceback.print_exc()
        print("No Samsung trade in button selection")
