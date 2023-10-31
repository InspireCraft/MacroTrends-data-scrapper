import unittest
from src.scrap_the_table import TableScrapper
import selenium
from selenium import webdriver
from selenium.webdriver.chrome import webdriver


class TableScrapperTestCase(unittest.TestCase):
    def setUp(self):
        self.scrapper = TableScrapper()
        self.driver = self.scrapper._create_driver()

    def test_create_driver(self):
        # Check if self.driver is a WebDriver object
        self.assertIsInstance(self.driver, selenium.webdriver.chrome.webdriver.WebDriver)

    def test_get_table_headers(self):
        self.header_list = self.scrapper._get_table_headers(self.driver)
        # Check if self.header_list is a dictionary
        self.assertIsInstance(self.header_list, dict)

        # Define what tabs have as headers
        overview = ['Stock Name\n(Hover for 1Y Chart)',
                     'Ticker',
                     'Industry',
                     'Market Cap',
                     'Closing\nPrice',
                     '1 Year\n% Change',
                     'P/E Ratio',
                     'Dividend\nYield']

        descriptive = ['Market Cap', 'Exchange', 'Country', 'Sector', 'Industry']
        dividend = ['Market Cap', 'Dividend\nYield', '12 Month\nDividend', '12 Month\nEPS',
                    'Dividend\nPayout Ratio']
        performance_st = ['1 Week\n% Change', '1 Month\n% Change', '3 Month\n% Change',
                          '6 Month\n% Change', 'YTD\n% Change', '1 Year\n% Change',
                          'Price vs\n50D SMA', 'Price vs\n200D SMA']

        performance_lt = ['3 Year\nCAGR %', '5 Year\nCAGR %', '10 Year\nCAGR %', '20 Year\nCAGR %',
                          '30 Year\nCAGR %', '40 Year\nCAGR %', '50 Year\nCAGR %']

        ratios_income = ['Price/Earnings\nRatio', 'PEG Ratio', 'Price/Sales\nRatio',
                         'Operating\nMargin', 'Pre-Tax\nMargin', 'Net Margin']

        ratios_debt = ['Price/Book\nRatio', 'Price/Cash\nRatio', 'Return\non Equity',
                       'Return\non Assets', 'Inventory\nTurnover', 'Current\nRatio',
                       'Quick\nRatio', 'Debt/Equity\nRatio']

        rev_earnings = ['12 Month\nSales Growth', '5 Year\nSales Growth', '12 Month\nEPS Growth',
                        '5 Year\nEPS Growth', 'Last Quarter\nEPS Surprise %',
                        'Estimated EPS\nGrowth Next Year']

        # Check if those headers corresponds to their tabs
        self.assertEqual(self.header_list["overview"], overview)
        self.assertEqual(self.header_list["descriptive"], descriptive)
        self.assertEqual(self.header_list["dividend"], dividend)
        self.assertEqual(self.header_list["performance_st"], performance_st)
        self.assertEqual(self.header_list["performance_lt"], performance_lt)
        self.assertEqual(self.header_list["ratios_income"], ratios_income)
        self.assertEqual(self.header_list["ratios_debt"], ratios_debt)
        self.assertEqual(self.header_list["rev_earnings"], rev_earnings)

    def test_get_num_of_rows(self):
        (self.init, self.last, self.total) = self.scrapper._get_num_of_rows(self.driver)
        # Check if the row number types are integer
        self.assertIsInstance(self.init, int)
        self.assertIsInstance(self.last, int)
        self.assertIsInstance(self.total, int)

        # Check if self.init number = 1
        self.assertEqual(self.init, 1)

        # Check if self.last number = 20
        self.assertEqual(self.last, 20)

        # Check if self.total larger than the other two
        self.assertTrue(self.total > self.init)
        self.assertTrue(self.total > self.last)


if __name__ == "__main__":
    unittest.main()
