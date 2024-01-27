import tkinter as tk

from src.map_of_headers import MAP_OF_HEADERS


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

    def __init__(self):
        """Construct GUI frame, place button on it and initiate button list."""
        self.button_list = []  # List that holds what is clicked by th user

        # Create GUI frame (=window) with given name and Geometry
        self.window = tk.Tk(screenName="Parameters to Search")
        self.window.geometry("800x740")  # Width x Height
        self.window.title("SEARCH PARAMETERS")

        # Place all clickable buttons on the GUI frame
        self._place_buttons()

    def _change_button_state(self, button: tk.Button):
        """Change button state. If sunken, raise or vice versa.

        Parameters
        ----------
        button: tk.Button() object
            Button on the GUI

        """
        # Check the button state (sunken or raised). Alter the state.
        if button["relief"] == "sunken":
            button.config(relief="raised", bg="WHITE")  # Change button state: sunken -> raised
            # If already clicked button clicked again, remove the recorded item from the list
            self.button_list.remove(button.cget("text"))
        elif button["relief"] == "raised":
            button.config(relief="sunken", bg="GREEN")  # Change button state: raised -> sunken
            # If an unclicked button is clicked. Add the item into the list to record.
            self.button_list.append(button.cget("text"))
        else:
            raise ValueError("BUTTON STATE IS NEITHER SUNKEN NOR RAISED, IT IS UNKNOWN")

    def _close_window(self):
        """Kill GUI."""
        self.window.destroy()

    def _place_buttons(self):
        """Place clickable buttons on the GUI."""
        # Create "OK" button
        button_ok = tk.Button(
            self.window, text="OK", height=5, width=20, bg="RED", font="bold"
        )
        button_ok.grid(row=15, column=3)  # Position of the OK button

        # Get all the searchable elements
        search_params = [element for element in MAP_OF_HEADERS.keys()]

        cntx, cnty = 0, 0  # Initiate counters for button positioning on GUI
        cntx_max = 3
        for character in search_params:
            # Create searchable parameters buttons
            parameter_button = tk.Button(
                self.window, text=character, height=2, width=20, bg="WHITE", font="bold"
            )
            parameter_button.grid(row=cnty, column=cntx)  # Position it on the GUI

            # Below if else is only for positioning purposes
            if cntx < cntx_max:
                cntx += 1
            else:
                cntx = 0
                cnty += 1

            # When parameter button is clicked, change the state
            parameter_button.config(
                command=lambda button=parameter_button: self._change_button_state(button)
            )

            # When OK button is clicked, direct GUI to its kill method
            button_ok.config(
                command=self._close_window
            )

    def run_gui(self) -> list[str]:
        """Run GUI loop. Record what was clicked by user and save them in a JSON."""
        self.window.mainloop()  # Initiate GUI loop
        return self.button_list


def main():
    """Run GUI."""
    cl = TableScrapperGUI()
    params_to_be_searched = cl.run_gui()
    print(params_to_be_searched)


if __name__ == "__main__":
    main()
