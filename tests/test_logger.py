import unittest
from unittest.mock import patch, Mock
from src.utils.Logger import Logger


class TestLogger(unittest.TestCase):
    """Test the Logger class."""

    @patch("logging.StreamHandler")
    def test_constructor(self, mock_stream_handler):
        """Check the Logging class is set properly.

        logging.StreamHandler is mocked such that whenever it is called, return value creates Mock()
        object.
        """
        mock_handler = Mock()
        mock_stream_handler.return_value = mock_handler

        logger = Logger("test_logger")

        # Verify that the StreamHandler is added to the logger's handlers
        self.assertIn(mock_handler, logger.handlers)

        # Assert the logging level of the created logger
        self.assertEqual(logger.level, Logger.logger_level_dict["none"])

    @patch('logging.FileHandler')
    def test_log_to_file(self, mock_file_handler):
        """Check whether adding a file handler works properly."""
        mock_file = Mock()
        mock_file_handler.return_value = mock_file

        logger = Logger('test_logger', 'none')
        filename = 'test.log'
        logger.log_to_file(filename)
        # Verify that the handlers are added to the logger's handlers
        self.assertIn(mock_file, logger.handlers)

    @patch('logging.Logger.info')
    def test_info(self, mock_logging):
        """Test functionality for .info() with info level."""
        logger = Logger('test_logger', 'info')
        expected_message = "info"
        logger.info(expected_message)
        # Check if logging.info has been called with the expected message
        mock_logging.assert_called_once_with(expected_message)

    @patch('logging.Logger._log')
    def test_wrong_level(self, mock_logging):
        """Test functionality for .info() with none level. _log should not be called."""
        logger = Logger('test_logger', 'none')
        expected_message = "info"
        logger.info(expected_message)
        # Check if logging.info has been called with the expected message
        mock_logging.assert_not_called()


if __name__ == "__main__":
    unittest.main()
