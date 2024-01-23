# Import libraries
import os
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from src.map_of_headers import MAP_OF_HEADERS
from src.utils.Logger import Logger
from src.utils.manage_driver import DriverManager
from src.gui_scrap_the_table import TableScrapperGUI


class TableScrapper:
    """
    Class to be used to scrap the table data in macro-trends.

    Attributes
    ----------
    tab_names : list of str
        list of the names of the table tabs

    logger : Logger object

    Methods
    -------
    scrap_the_table():
        return the table data in dictionary format

    """

    def __init__(self, str_logger="info"):
        """
        Construct instant variables.

        Parameters
        ----------
        str_logger : str
              the functionality string of the logger object
        """
        # URL of the website this table scrapper works
        url = "https://www.macrotrends.net/stocks/stock-screener"

        self.driver_manager = DriverManager()  # Initialize driver manager object
        self.driver_manager.set_up_driver(url=url)  # Set up the driver by using the url
        self.logger = Logger(self.__class__.__name__, str_logger)

        # Call TableScrapperGUI
        gui = TableScrapperGUI()
        gui.forward()  # Make user select what is desired to be searched

        # Read JSON file for parameters required to be searched
        path_for_search_parameters = os.path.dirname(os.path.abspath(__file__))
        with open(f"{path_for_search_parameters}/searchParameters.json") as parameters_to_search:
            search_dict = json.load(parameters_to_search)

        # Sort search parameters for efficient interaction with the website
        self.search_params = self._sort_search_parameters(search_dict)

        # Print to CL what is searched
        self.logger.info(f"Search Params = {self.search_params}...")

    @staticmethod
    def _sort_search_parameters(search_dict):
        """Sort tab_names for min amount of click interaction.

        Parameters
        ----------
        search_dict : dict
            dictionary of parameters

        Returns
        -------
        Sorted list of parameters to be scrapped
        """
        parameters = [element for element in search_dict["search_parameters"]]

        # Get required tab_names to be clicked to search for parameters
        tab_name_list = [
            list(MAP_OF_HEADERS[element].keys())[0] for element in search_dict["search_parameters"]
        ]
        # Re-order parameters for efficient search (this allows less click interaction)
        # Below line of code re-order parameter list such a way that the parameters
        # sharing the same tab_name grouped together
        # sorted(zip(param1,param2)) sorts according to param1
        return [p for _, p in sorted(zip(tab_name_list, parameters))]

    @staticmethod
    def _get_num_of_rows(driver) -> "tuple[int,int,int]":
        """Check current row number, max row number in current page, total row number.

        Parameters
        ----------
        driver : WebDriver object

        Returns
        -------
        current_initial_number, current_final_number, number_of_rows_in_the_list : tuple of ints

        """
        temp = driver.find_elements(By.XPATH, "// *[ @ id = 'pagerjqxGrid'] / div / div[6]")
        current_initial_number = int(temp[0].text.split("-")[0])
        current_final_number = int(temp[0].text.split("-")[1].split(" ")[0])
        number_of_rows_in_the_list = int(temp[0].text.split("-")[1].split(" ")[2])
        return current_initial_number, current_final_number, number_of_rows_in_the_list

    def __del__(self):
        """Shut down the driver."""
        self.driver_manager.kill_driver()

    def scrap_the_table(self):
        """Scrap the whole table including all tabs and pages in macro-trend.

        Parameters
        ----------
        None

        Returns
        -------
        company_attr_dict : dict
            dictionary of the companies associated with their properties
        """
        # Let scrapping begin
        self.logger.info("SCRAPPING STARTED...")

        # Get number of rows per page and total
        (init_num, final_num, max_num) = self._get_num_of_rows(self.driver_manager.driver)

        # Initialize attribute dictionary
        company_attr_dict = {}

        with tqdm(total=max_num) as pbar:
            while final_num != max_num:
                (init_num, final_num, _) = self._get_num_of_rows(
                    self.driver_manager.driver
                )
                num_of_companies_on_page = final_num - init_num + 1

                ticker_list = []
                # Pre-set the company tickers
                for row_index in range(num_of_companies_on_page):
                    # Get company tickers
                    company_ticker = (
                        self.driver_manager.driver.find_elements(
                            By.XPATH, f"// *[ @ id = 'row{row_index}jqxGrid'] / div[2] / div")[
                            0].text)
                    company_attr_dict[company_ticker] = {}

                    # Get company names
                    company_name = self.driver_manager.driver.find_elements(
                        By.XPATH, f"//*[@id='row{row_index}jqxGrid']/"
                                  f"div[1]/div/div/a")[0].text
                    company_attr_dict[company_ticker]['name'] = company_name

                    # Store by-for-loop company tickers
                    ticker_list.append(company_ticker)

                # For each parameter to be scrapped, fill the dictionary
                previous_tab_name = None
                for param in self.search_params:
                    # Click the corresponding header
                    tab_name, column_index = list(MAP_OF_HEADERS[param].items())[0]
                    column_index -= 1

                    # Check if clicking onto a tab name is required
                    if previous_tab_name != tab_name:
                        WebDriverWait(self.driver_manager.driver, 10).until(
                            ec.element_to_be_clickable(
                                (By.XPATH, f"//*[@id='columns_{tab_name}']/a")
                            )
                        ).click()

                        previous_tab_name = tab_name

                    # Fill dictionary ticker by ticker
                    for ticker, row_index in zip(ticker_list, range(num_of_companies_on_page)):
                        # Get parameter values
                        parameter_value = self.driver_manager.driver.find_elements(
                            By.XPATH,
                            f"//*[@id='row{row_index}jqxGrid']/"
                            f"div[{int(3 + column_index)}]/div"
                        )[0].text
                        company_attr_dict[ticker][param] = parameter_value

                # Update the progress bar
                pbar.update(int(num_of_companies_on_page))

                # Click on the clickable arrow on the table to progress in the pages
                WebDriverWait(self.driver_manager.driver, 2).until(
                    ec.element_to_be_clickable(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div[4]/div[2]/div/div/div/div/div[10]/div/div[4]/div"
                        )
                    )
                ).click()

        self.logger.info("SCRAPPING IS DONE!!!")
        self.logger.info(f"SCRAPPED DATA: {self.search_params} ")

        return company_attr_dict


def main():
    """Run the TableScrapper.

    Returns
    -------
    scrapped_data : dict
        Dictionary of the table in the given url
    """
    import csv
    scrapper = TableScrapper()
    scrapped_data = scrapper.scrap_the_table()
    with open('scrap_table_trial.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in scrapped_data.items():
            writer.writerow([key, value])


if __name__ == "__main__":
    main()
