import csv
import os
import unittest

from src.data_recorder import DataRecorder


class TestDataRecorder(unittest.TestCase):
    """Unit tests for the DataRecorder class."""

    def setUp(self):
        """Set up the test environment."""
        self.csv_file_name = "test_data.csv"
        self.data_recorder = DataRecorder(self.csv_file_name)

    def tearDown(self):
        """Tear down the test environment."""
        if os.path.exists(self.csv_file_name):
            os.remove(self.csv_file_name)

    def test_save_to_csv(self):
        """Test the save_to_csv method of DataRecorder."""
        # Test with empty CSV file
        scrapped_data = {
            "AAPL": {"MarketCap": 100},
            "GOOGL": {"MarketCap": 200}
        }
        self.data_recorder.save_to_csv(scrapped_data)

        # Check if the CSV file is created
        self.assertTrue(os.path.exists(self.csv_file_name))

        # Check if headers are written correctly
        with open(self.csv_file_name, "r") as file:
            reader = csv.reader(file)
            headers = next(reader)
            self.assertEqual(headers, ['Ticker', 'MarketCap'])

        # Check if data is written correctly
        with open(self.csv_file_name, "r") as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]['Ticker'], 'AAPL')
