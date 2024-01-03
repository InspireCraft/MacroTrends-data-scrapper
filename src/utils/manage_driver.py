from src.utils.create_driver import create_driver


class DriverManager:
    """Class to set up and kill driver.

    Methods
    -------
    set_up_driver():
        Set up driver object for the url given

    kill_driver():
        Kill driver object
    """

    def __init__(self):
        self.driver = create_driver(logger_str="none")

    def set_up_driver(self, url):
        """Set up driver object for the url given.

        Parameters
        ----------
        url : string
            url of the website to be scrapped

        """
        self.driver.get(url)

    def kill_driver(self):
        """Kill driver object."""
        self.driver.close()
        self.driver.quit()


def main():
    """Run set up driver function."""
    url = "https://www.macrotrends.net/stocks/stock-screener"
    drv_ctrl = DriverManager()
    drv_ctrl.set_up_driver(url)
    drv_ctrl.kill_driver()


if __name__ == "__main__":
    main()
