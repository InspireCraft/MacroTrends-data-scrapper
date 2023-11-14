from selenium.webdriver.chrome.options import Options
from selenium import webdriver


def create_driver(url, logger) -> "webdriver.chrome":
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
    logger.info("WebDriver is being created...")
    options = Options()
    options.add_argument("--headless")  # Run selenium without opening an actual browser

    driver = webdriver.Chrome(options=options)  # Initialize the driver instance
    driver.get(url)
    logger.info("WebDriver is created!!!")
    return driver