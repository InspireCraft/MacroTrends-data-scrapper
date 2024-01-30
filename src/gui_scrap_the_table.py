import tkinter as tk
import os

from src.map_of_headers import MAP_OF_HEADERS

# # The code below enables test of this class to run on GitHub
# if os.environ.get("DISPLAY", "") == "":
#     os.environ.__setitem__("DISPLAY", ":0.0")


class TableScrapperGUI:
    """
    Class to be used as GUI which enables user to select parameters to be searched.

    Methods
    -------
    _change_button_state(button):
        Alter button state after click. If it is sunken, raise or vice versa.

    _close_window(win):
        Kill GUI

    _place_buttons():
        Create GUI frame and place all selectable in it.

    run_gui():
        Start GUI, record what is clicked by user (only sunken) and save them in a JSON file.
    """

    def __init__(self, screen_name="Parameters to Search", geometry="800x740", title="SEARCH PARAMETERS"):
        """Construct GUI frame, place button on it and initiate button list."""
        self.window = tk.Tk(screenName=screen_name)
        self.window.geometry(geometry)  # Width x Height
        self.window.title(title)

        self.sunken_button_list = []

    def _record_clicked_buttons(self, button):
        """Record clicked buttons."""
        text = button.cget("text")  # Get the text on the button
        # This function is called when a button is clicked.
        # It records the text on the clicked button.
        # if the text on the button is already in the list, it means
        # that it was already clicked before, so it is clicked again
        # Therefore, this function checks if the text on the button is
        # in the list, and if so, it removes from the list, if not, it adds
        # to the list
        if text in self.sunken_button_list:
            self.sunken_button_list.remove(text)
        else:
            self.sunken_button_list.append(text)

    @staticmethod
    def _change_button_state(button: tk.Button):
        """Change button state. If sunken, raise or vice versa.

        Parameters
        ----------
        button: tk.Button() object
            Button on the GUI

        """
        # Check the button state (sunken or raised). Alter the state.
        if button["relief"] == "sunken":
            button.config(relief="raised", bg="WHITE")  # Change button state: sunken -> raised
        elif button["relief"] == "raised":
            button.config(relief="sunken", bg="GREEN")  # Change button state: raised -> sunken
        else:
            raise ValueError("BUTTON STATE IS NEITHER SUNKEN NOR RAISED, IT IS UNKNOWN")

    def _close_window(self):
        """Kill GUI."""
        self.window.destroy()

    def _create_buttons(self, search_params):
        # Initiate button dictionary
        button_dictionary = {}

        # Create buttons for paramaters to be searched
        for txt in search_params:
            button_dictionary[txt] = tk.Button(
                self.window, text=txt, height=2, width=20, bg="WHITE", font="bold"
            )
            # assume:  x = button_dictionary[txt]
            # The difference between:
            # lambda x: func(x)   and   lambda a=x : func(a)
            #
            # In the first one, x is a free variable bound at execution time of lambda expression
            # Lambda function captures x at run time. At run time, the value of x is the latest
            # search_params. Therefore, change_button_state function is only valid for
            # button_dictionary[search_params[-1]]
            #
            # In the second one,lambda function is initialized with a default value x.
            # I.e., corresponding button_dictionary[txt]
            # When executed, in run-time, it is called with its default value.
            # Therefore, change_button_state function is valid for each button
            button_dictionary[txt].config(
                command=lambda button=button_dictionary[txt]: [
                    self._change_button_state(button),
                    self._record_clicked_buttons(button)
                ]
            )

        # Create "OK" button
        button_dictionary["OK"] = tk.Button(
            self.window, text="OK", height=5, width=20, bg="RED", font="bold"
        )

        # When OK button is clicked, direct GUI to its kill method
        button_dictionary["OK"].config(
            command=self._close_window
        )
        return button_dictionary

    @staticmethod
    def _place_buttons(button_dictionary):
        """Place clickable buttons on the GUI."""
        # Position of the OK button
        ok_button_position_row = 15  # Row position
        ob_button_position_column = 3  # Column position
        button_dictionary["OK"].grid(
            row=ok_button_position_row,
            column=ob_button_position_column
        )

        # Initiate position counters for parameter button
        parameter_button_position_row = 0
        parameter_button_position_column = 0

        # Set maximum number of columns
        parameter_button_position_column_max = 3

        # Start positioning the buttons
        search_params = list(button_dictionary.keys())
        search_params.remove("OK")
        for txt in search_params:
            button_dictionary[txt].grid(
                row=parameter_button_position_row,
                column=parameter_button_position_column
            )  # Position it on the GUI

            # Below if else is only for positioning purposes
            if parameter_button_position_column < parameter_button_position_column_max:
                parameter_button_position_column += 1
            else:
                parameter_button_position_column = 0
                parameter_button_position_row += 1

    def run_gui(self, search_params ) -> list[str]:
        """Run GUI loop. Record what was clicked by user and save them in a JSON."""

        button_dictionary=self._create_buttons(search_params)
        self._place_buttons(button_dictionary)
        self.window.mainloop()  # Initiate GUI loop
        return self.sunken_button_list


def main():
    """Run GUI."""
    search_params = [element for element in MAP_OF_HEADERS.keys()]
    gui = TableScrapperGUI()
    parameters_to_be_searched = gui.run_gui(search_params)
    print(parameters_to_be_searched)


if __name__ == "__main__":
    main()
