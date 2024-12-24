from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from stealthenium import stealth

from constants import USER_AGENT, WEB_DRIVER_PORT


def get_new_driver() -> WebDriver:
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-agent={USER_AGENT}")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # headless does not work for BestBuy
    # options.add_argument("--headless=new")

    # to keep browser open for testing (also comment driver.quit() at end of script)
    # options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(
        options=options, service=webdriver.ChromeService(port=WEB_DRIVER_PORT)
    )
    driver.command_executor._url = f"http://localhost:{WEB_DRIVER_PORT}"

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
