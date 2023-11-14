import unittest
from unittest.mock import patch
from src.financials_scrapper import FinancialDataScraper


class TestFinancialDataScraper(unittest.TestCase):
    """Test the FinancialDataScraper class."""

    def setUp(self):
        """Set up before each test."""
        self.logging_level_str = "debug"

    @patch("logging.Logger._log")
    @patch("selenium.webdriver.Chrome")
    def test_constructor(self, mock_webdriver_fn, mock_logger_fn):
        """Check the FinancialDataScraper class is set properly."""
        financial_scrapper = FinancialDataScraper(self.logging_level_str)
        self.assertTrue(mock_webdriver_fn.called)
        self.assertTrue(mock_logger_fn.called)
        self.assertEqual(len(financial_scrapper._row_indices), 0)


if __name__ == "__main__":
    unittest.main()
