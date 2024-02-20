import tkinter as tk

from src.map_of_headers import MAP_OF_HEADERS


class TableScrapperGUI:
    """
    Class to be used as GUI which enables user to select parameters to be searched.

    Methods
    -------
    _set_up_gui():
        Create and Place the buttons on the gui

    _record_clicked_buttons(button):
        Record clicked buttons.

    _create_buttons(button_text):
        Generate buttons associating with their texts.

    _change_button_state(button):
        Alter button state after click. If it is sunken, raise or vice versa.

    _close_window(win):
        Kill GUI

    _place_buttons():
        Place clickable buttons on the GUI.

    run_gui():
        Start GUI, record what is clicked by user (only sunken) and return it.
    """

    def __init__(self,
                 screen_name="Parameters to Search",
                 geometry="800x740",
                 title="SEARCH PARAMETERS"):
        """Construct GUI frame, and initiate a list that records sunken button."""
        self.window = tk.Tk(screenName=screen_name)
        self.window.geometry(geometry)  # Width x Height
        self.window.title(title)

        # Set up the GUI
        self._set_up_gui()

        # Initiate a list that records the texts of the sunken buttons
        self.sunken_button_list = []

    def _set_up_gui(self):
        """Create and Place the buttons on the gui."""
        # Get parameters that are desired to be scrapped by the user
        search_params = [element for element in MAP_OF_HEADERS.keys()]

        # Create buttons for the GUI
        button_dictionary = self._create_buttons(search_params)

        # Place the buttons on the GUI frame
        self._place_buttons(button_dictionary)

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

    @staticmethod
    def _select_all(button_dict: dict):
        """When select all is clicked, change the states of the all buttons."""
        if button_dict["select_all"]["relief"] == "raised":
            button_dict["select_all"].config(relief="sunken", bg="GREEN")
            select_all_is_clicked = True
        else:
            button_dict["select_all"].config(relief="raised", bg="WHITE")
            select_all_is_clicked = False

        if select_all_is_clicked:
            for key in list(button_dict.keys()):
                if key == "OK":
                    continue
                else:
                    button_dict[key].config(relief="sunken", bg="GREEN")
        else:
            for key in list(button_dict.keys()):
                if key == "OK":
                    continue
                else:
                    button_dict[key].config(relief="raised", bg="WHITE")

    def _record_clicked_buttons(self, button_dict: dict):
        """Record all sunken (=clicked) buttons after OK is clicked."""
        for key in list(button_dict.keys()):
            if key == "OK" or key == "select_all":
                continue
            else:
                if button_dict[key]["relief"] == "sunken":
                    text = button_dict[key].cget("text")
                    self.sunken_button_list.append(text)
        # Then close the GUI
        self._close_window()

    def _close_window(self):
        """Kill GUI."""
        self.window.destroy()

    def _create_buttons(self, button_text):
        """Generate buttons associating with their texts.

        Returns
        -------
        button_dictionary : dict[tk.Button]
            Dictionary of buttons. Keys are the texts of the buttons
        """
        # Initiate button dictionary
        button_dictionary = {}

        # Create buttons for each text given by the user
        for txt in button_text:
            button_dictionary[txt] = tk.Button(
                self.window, text=txt, height=2, width=20, bg="WHITE", font="bold"
            )
            # assume:  x = button_dictionary[txt]
            # The difference between:
            # lambda x: func(x)   and   lambda a=x : func(a)
            #
            # In the first one, x is a free variable bound at execution time of lambda expression
            # Lambda function captures x at run time. At run time, the value of x is the latest
            # button_text. Therefore, change_button_state function is only valid for
            # button_dictionary[button_text[-1]]
            #
            # In the second one,lambda function is initialized with a default value x.
            # I.e., corresponding button_dictionary[txt]
            # When executed, in run-time, it is called with its default value.
            # Therefore, change_button_state function is valid for each button
            button_dictionary[txt].config(
                command=lambda button=button_dictionary[txt]: [
                    self._change_button_state(button),
                ]
            )

        # Create "OK" button
        button_dictionary["OK"] = tk.Button(
            self.window, text="OK", height=5, width=20, bg="RED", font="bold"
        )

        # When OK button is clicked, direct GUI to its kill method
        button_dictionary["OK"].config(
            command=lambda: self._record_clicked_buttons(button_dictionary),
        )

        # Create "SELECT ALL" button
        button_dictionary["select_all"] = tk.Button(
            self.window, text="SELECT ALL", height=5, width=20, bg="WHITE", font="bold"
        )

        # When "SELECT ALL" button is clicked, Make all parameter buttons raised or sunken
        button_dictionary["select_all"].config(
            command=lambda: self._select_all(button_dictionary)
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

        # Position of the SelectAll button
        select_all_button_position_row = 15  # Row position
        select_all_button_position_col = 2  # Column position
        button_dictionary["select_all"].grid(
            row=select_all_button_position_row,
            column=select_all_button_position_col
        )

        # Initiate position counters for parameter button
        parameter_button_position_row = 0
        parameter_button_position_column = 0

        # Set maximum number of columns
        parameter_button_position_column_max = 3

        # Start positioning the buttons
        search_params = list(button_dictionary.keys())
        search_params.remove("OK")
        search_params.remove("select_all")
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

    def run_gui(self) -> list[str]:
        """Run GUI loop. Record what was clicked by user and return it.

        Returns
        -------
        self.sunken_button_list : list[str]
            list of clicked buttons
        """
        self.window.mainloop()  # Initiate GUI loop
        return self.sunken_button_list


def main():
    """Run GUI."""
    gui = TableScrapperGUI()
    parameters_to_be_scrapped = gui.run_gui()
    print(parameters_to_be_scrapped)


if __name__ == "__main__":
    main()
