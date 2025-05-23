import time
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from amazon_captcha import amazon_captcha_required, solve_amazon_captcha
from automation import click_samsung_no_trade_in_button
from walmart_captcha import solve_walmart_captcha, walmart_captcha_required


def get_price(driver: WebDriver, product_dict: dict) -> dict:
    price = -1
    error = False
    info = "OK"

    try:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    except:
        pass

    if "amazon.com" in product_dict["url"]:
        store = "Amazon"
        #css_selector = "#newAccordionRow_0 #corePrice_feature_div span.a-offscreen"
        css_selector = "#apex_offerDisplay_desktop #corePrice_feature_div span.a-offscreen"
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
        #css_selector = ".DeviceTile_selected__H71O3 .DeviceTile_device__price___rO94"
        css_selector = ".PriceInfoText_priceInfo__pAyUK:not(:has(.terms)"
    elif "homedepot.com" in product_dict["url"]:
        store = "Home Depot"

        # Home Depot splits the price to 2 span elements. 1 has high order amount and other has low order amount.
        # Custom handling of this is done below
        css_selector = ""
    elif "musiciansfriend.com" in product_dict["url"]:
        store = "Musician's Friend"
        css_selector = ".price-display .price-display_markup"
    elif "guitarcenter.com" in product_dict["url"]:
        store = "Guitar Center"
        #css_selector = "#PDPRightRailWrapper .sale-price"
        css_selector = ".pdp-price-wrap span"
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
            try:
                driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
            except:
                pass

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
                captcha_required = WebDriverWait(driver, 10).until(
                    amazon_captcha_required
                )
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
                captcha_required = WebDriverWait(driver, 10).until(
                    walmart_captcha_required
                )
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
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            ".sui-text-9xl.sui--translate-y-\\[0\\.5rem\\]",
                        )
                    )
                )

                price_high_order = price_high_order_element.get_attribute("textContent")

                price_low_order_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".sui-sr-only + .sui-text-3xl")
                    )
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
                if "musiciansfriend.com" in product_dict["url"]:
                    # first is screen reader price -- second is displayed price
                    if len(price.split()) > 1:
                        price = price.split()[1]

                price = price.lower().strip()
                price = price.replace("$", "")
                price = price.replace(
                    "now", ""
                )  # remove Now prefix from Walmart element that sometimes exists
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
