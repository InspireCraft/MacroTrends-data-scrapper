import unittest
from src.scrap_the_table import TableScrapper
from src.map_of_headers import MAP_OF_HEADERS


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
        self.scrapper = TableScrapper(params_to_be_searched=["Market Cap"], str_logger="none")
        self.driver = self.scrapper.driver_manager.driver

    def test_sort_search_parameters(self):
        """Check if sorting works."""
        search_parameters = [
                "Market Cap",
                "3 Year CAGR %",
                "5 Year CAGR %",
                "Price/Earnings Ratio",
                "PEG Ratio",
                "Closing Price",
                "1 Year % Change",
                "30 Year CAGR %"
            ]

        search_params = self.scrapper._sort_search_parameters(search_parameters)

        # Get headers after sorting/grouping
        header_list = [list(MAP_OF_HEADERS[name].keys())[0] for name in search_params]

        # Re-sort the headers to check if any unexpected situation exists
        list_tobe_sort = header_list.copy()
        list_tobe_sort = sorted(list_tobe_sort)

        # Assert if the two list equal
        self.assertEqual(header_list, list_tobe_sort)

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
