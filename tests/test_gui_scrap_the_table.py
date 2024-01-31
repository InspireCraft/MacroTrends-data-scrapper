import unittest
import tkinter as tk
import os

from src.gui_scrap_the_table import TableScrapperGUI


class TestCreateDriver(unittest.TestCase):
    """Class to be used to test CreateDriver function.

    Methods
    -------
    test_create_drivers():
        check if the created driver object is WebDriver object
    """

    def setUp(self) -> None:
        """Set up display."""
        os.environ['DISPLAY'] = ':99'

    def test_change_button_state(self):
        """Check button relief before and after it is clicked."""
        dummy_button = tk.Button()  # Initialize dummy button

        # When initialized, the button is in "raised" state
        self.assertEqual(dummy_button["relief"], "raised")

        # Pass the button through the function
        TableScrapperGUI._change_button_state(dummy_button)
        # Check if it altered its state
        self.assertEqual(dummy_button["relief"], "sunken")

        # Pass the button through the function again
        TableScrapperGUI._change_button_state(dummy_button)
        # Check if it altered its state
        self.assertEqual(dummy_button["relief"], "raised")


if __name__ == "__main__":
    unittest.main(warnings='ignore')
