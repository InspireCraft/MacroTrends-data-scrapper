from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def set_driver(url='https://www.macrotrends.net/stocks/stock-screener'):
    """
    Set driver settings.

    Parameters
    ----------
    url : str
        website

    Returns
    -------
    driver : obj
        WebDriver object
    """
    print('Driver is being set...')
    options = Options()
    options.add_argument("--headless")  # Run selenium under headless mode

    driver = webdriver.Chrome(options=options)  # Initialize the driver instance
    driver.get(url)
    print('Driver is set!!!')
    return driver
