from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from src.utils.Logger import Logger
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import json
import os

def create_driver(url, logger_str="info") -> "webdriver.chrome":
    """Create driver object.

    Driver is an WebDriver object that interacts with the website. Clicking,
    reading are the methods of the driver object.

    Parameters
    ----------
    url : string
        url of the website which is going to be scrapped

    logger : Logger object

    Returns
    -------
    driver : WebDriver object

    """
    logger = Logger("create_driver", logger_str)
    logger.info("WebDriver is being created...")

    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    f_search = open("..\\src\\utils\\webdriverOptions.json")
    options_dict = json.load(f_search)
    f_search.close()

    # Get desired webdriver options
    opts = [opt for opt in options_dict["options"]]
    logger.info(f"Webdriver Options = {opts}...")

    # Add driver options to the driver
    options = Options()
    for opt in opts:
        options.add_argument(opt)

    driver = webdriver.Chrome(options=options)

    # Finalize driver creation by calling the url
    driver.get(url)
    logger.info("WebDriver is created!!!")
    return driver

def main():
    return create_driver(url="https://www.macrotrends.net/stocks/stock-screener")

if __name__ == "__main__":
    driver = main()
    driver.close()
    driver.quit()
