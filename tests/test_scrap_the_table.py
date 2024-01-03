import unittest
from src.scrap_the_table import TableScrapper


class TestTableScrapper(unittest.TestCase):
    """Class to be used to test TableScrapper class.

    Methods
    -------
    setUP():
        setUp reused variables/objects

    test_create_drivers():
        check if the created driver object is WebDriver object

    test_get_table_headers():
        check if function return a dictionary
        check if all the headers (corresponding to tabs) are scrapped or not

    test_get_num_of_rows():
        check if the function returns tuple of ints
        check the returned numbers corresponds to some specific integers
        check the magnitude relationship of the numbers
    """

    def setUp(self):
        """Set up reused variables/objects."""
        url = 'https://www.macrotrends.net/stocks/stock-screener'
        self.scrapper = TableScrapper(url=url, str_logger="none")
        self.driver = self.scrapper.driver_manager.driver

    def test_get_num_of_rows(self):
        """Check if the function returns tuple of ints.

        Check the returned numbers corresponds to some specific integers
        Check the magnitude relationship of the numbers

        """
        (init, last, total) = self.scrapper._get_num_of_rows(self.driver)
        # Check if the row number types are integer
        self.assertIsInstance(init, int)
        self.assertIsInstance(last, int)
        self.assertIsInstance(total, int)

        # Check if self.init number = 1
        self.assertEqual(init, 1)

        # Check if self.last number = 20
        self.assertEqual(last, 20)

        # Check if self.total larger than the other two
        self.assertTrue(total > init)
        self.assertTrue(total > last)


if __name__ == "__main__":
    unittest.main()
