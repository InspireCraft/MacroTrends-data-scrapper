import tkinter as tk
from map_of_headers import MAP_OF_HEADERS


class GUI():
    def __init__(self):
        self.but_list = []
        self.window = tk.Tk(screenName="Parameters to Search")
        self.window.geometry("640x640")  # Width x Height
        self.window.title("SEARCH PARAMETERS")
        self.place_buttons()

    def change_button_state(self, button):
        if button["relief"] == "sunken":
            button.config(relief="raised")
            button.config(bg="WHITE")
            self.but_list.remove(button.cget("text"))
        elif button["relief"] == "raised":
            button.config(relief="sunken")
            button.config(bg="RED")
            self.but_list.append(button.cget("text"))
        else:
            print("BUTTON STATE IS UNKNOWN !!!")

    @staticmethod
    def close_window(win):
        win.quit()

    def place_buttons(self):
        button_ok = tk.Button(self.window, text="OK", height=5, width=20, bg="RED")
        button_ok.grid(row=15, column=3)
        search_params = [element for element in MAP_OF_HEADERS.keys()]
        cntx, cnty = 0, 0
        for character in search_params:
            # Create the button
            button_params = tk.Button(self.window, text=character, height=2, width=20, bg="WHITE")
            button_params.grid(row=cnty, column=cntx)
            if cntx < 3:
                cntx += 1
            else:
                cntx = 0
                cnty += 1

            # Add the command attribute to the button
            button_params.config(command=lambda button=button_params: self.change_button_state(button))
            button_ok.config(command=lambda win=self.window: self.close_window(win))

    def forward(self):
        self.window.mainloop()


def main():
    cl = GUI()
    cl.forward()
    print(cl.but_list)


if __name__ == "__main__":
    main()
