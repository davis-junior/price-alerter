# pip install amazoncaptcha requests selenium stealthenium

# TODO: implement Walmart robot or human solver

from pprint import pprint
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


    # Home products
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
    # return 1 if there are at least 2 error records of the product and store that have
    # been recorded in the 8 hours
    sql = """
    --begin-sql
        SELECT 1
        FROM pricelog
        WHERE product_name = ?
            AND store = ?
            AND status = 'ERROR'
            AND timestamp_added BETWEEN datetime(current_timestamp, '-8 hours', 'localtime') AND datetime(current_timestamp, 'localtime')
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


def main():
    while True:
        try:
            with sqlite3.connect("price_scraper.db", isolation_level=None) as conn:
                cursor = conn.cursor()

                create_tables(cursor)

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

                try:
                    results = []
                    for product_dict in products:
                        # add additional wait time for Walmart
                        if "walmart.com" in product_dict["url"]:
                            print("Current product is at Walmart. Waiting an additional 60 seconds before loading page...")
                            time.sleep(62)
                        
                        result = get_price(driver, product_dict)
                        if result:
                            results.append(result)

                        print("Waiting 60 seconds...")
                        time.sleep(62)
                except:
                    traceback.print_exc()
                finally:
                    driver.quit()

                record_and_output_results(cursor, results)
                notify_when_below_target(cursor, results)
        except:
            traceback.print_exc()

        # wait about an hour
        print("Waiting about 1 hour...")
        time.sleep(3600 + 120)


if __name__ == '__main__':
    main()
