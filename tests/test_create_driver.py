import unittest
from src.utils.create_driver import create_driver
from src.utils.Logger import Logger
import selenium


class TestCreateDriver(unittest.TestCase):
    """Class to be used to test CreateDriver function.

    Methods
    -------
    test_create_drivers():
        check if the created driver object is WebDriver object
    """

    def setUp(self) -> None:
        """Set up parameters."""
        self.logger = Logger("unittest_create_driver", "info")

    def test_create_driver(self):
        """Check if the created driver object is WebDriver object."""
        # Check if self.driver is a WebDriver object
        driver = create_driver(logger_str="none")
        self.assertIsInstance(driver, selenium.webdriver.chrome.webdriver.WebDriver)
        driver.close()
        driver.quit()


if __name__ == "__main__":
    unittest.main(warnings='ignore')
