import unittest
from src.utils.manage_driver import ManageDriver


class TestManageDriver(unittest.TestCase):
    """Class to be used to test ManageDriver class and its methods

    Methods
    -------
    setUp():
        setUp reused variables/objects

    test_set_up_driver():
        test set_up_driver method, check if driver gets url or not

    test_kill_driver():
        test kill_driver method, check if driver is shutdown
    """

    def setUp(self):
        """Set up reused variables/objects."""
        self.driver_controller = ManageDriver()

    def test_set_up_driver(self):
        """Check if the driver gets the url."""
        url = "https://www.macrotrends.net/stocks/stock-screener"
        self.driver_controller.set_up_driver(url)
        self.assertTrue(self.driver_controller.driver.current_url == url)

    def test_kill_driver(self):
        """Check if the driver is shut down."""
        self.driver_controller.kill_driver()
        self.assertFalse(self.driver_controller.driver.service.is_connectable())


if __name__ == "__main__":
    unittest.main()
