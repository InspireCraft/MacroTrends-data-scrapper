import unittest
import tkinter as tk

from src.gui_scrap_the_table import TableScrapperGUI


class TestCreateDriver(unittest.TestCase):
    """Class to be used to test CreateDriver function.

    Methods
    -------
    test_create_drivers():
        check if the created driver object is WebDriver object
    """

    def setUp(self) -> None:
        """Set up parameters."""
        self.gui = TableScrapperGUI()

    # def tearDown(self) -> None:
    #     """Kill GUI."""
    #     self.gui._close_window()

    def test_change_button_state(self):
        """Check button relief before and after it is clicked."""
        dummy_button = tk.Button()
        dummy_button.config(
            command=lambda button=dummy_button: self.gui._change_button_state(button)
        )
        # When not clicked, button should be raised
        self.assertEqual(dummy_button["relief"], "raised")

        # Click the button
        dummy_button.invoke()

        # After it is clicked it should be sunken
        self.assertEqual(dummy_button["relief"], "sunken")

        # Click the button again
        dummy_button.invoke()

        # If it is sunken, button should be raised after the click
        self.assertEqual(dummy_button["relief"], "raised")


if __name__ == "__main__":
    unittest.main(warnings='ignore')
