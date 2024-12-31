# TODO: record notifications sent and type in new table and use this instead

import random
import sqlite3
import time
import traceback

from selenium.webdriver.support.ui import WebDriverWait

from cli import main as cli_main
from constants import PRODUCTS, DB_FILE_NAME
from db import create_tables
from driver import get_new_driver
from globals import config_dict
from graphs import create_graphs
from notifications import notify_when_below_target_or_error
from scraping import get_price
from util import record_and_output_results
from walmart_captcha import walmart_captcha_required, solve_walmart_captcha
from web import create_html


def get_all_prices():
    results = []
    for product_dict in PRODUCTS:
        try:
            print("Getting new driver...")
            driver = get_new_driver()

            result = get_price(driver, product_dict)
            if result:
                results.append(result)

            # even if price is retrieved on Walmart now, sometimes the CAPTCHA shows up to 10 seconds after page load
            # just check and solve if so
            if "walmart.com" in product_dict["url"]:
                if result["current_price"] != -1:
                    print("Even though found price, checking Walmart CAPTCHA again...")
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
        except:
            traceback.print_exc()
        finally:
            time.sleep(2)
            print("Quitting driver...")
            driver.quit()

        print("Waiting about a minute...")
        time.sleep(60 + random.randint(3, 15))

    return results


def is_config_setup():
    return config_dict["ntfy_channel"] and config_dict["ntfy_channel"].strip()


def main():
    if not is_config_setup():
        print("ntfy channel not setup up. This is required. Redirecting to enter...")
        cli_main()

    if not is_config_setup():
        print("ntfy still not set up. Exiting program...")
        return

    while True:
        try:
            with sqlite3.connect(DB_FILE_NAME, isolation_level=None) as conn:
                cursor = conn.cursor()

                create_tables(cursor)

                graph_filenames = create_graphs(cursor)
                create_html(graph_filenames)

                results = get_all_prices()

                record_and_output_results(cursor, results)
                notify_when_below_target_or_error(cursor, results)

                graph_filenames = create_graphs(cursor)
                create_html(graph_filenames)
        except:
            traceback.print_exc()

        print("Waiting about an hour...")
        time.sleep(3600 + random.randint(180, 900))


if __name__ == "__main__":
    main()
