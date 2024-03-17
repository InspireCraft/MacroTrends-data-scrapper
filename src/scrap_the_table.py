# Import libraries
import csv
import os

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
    str_logger : str
        logger_level

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
        self.company_attr_dict = {}

    @staticmethod
    def _sort_search_parameters(params_to_be_searched):
        """Sort tab_names for min amount of click interaction.

        Parameters
        ----------
        params_to_be_searched : list[str]
            list of parameters

        Returns
        -------
        Sorted list of parameters to be scrapped
        """
        tab_name_list = [
            list(MAP_OF_HEADERS[element].keys())[0] for element in params_to_be_searched
        ]
        # Re-order parameters for efficient search (this allows less click interaction)
        # Below line of code re-order parameter list such a way that the parameters
        # sharing the same tab_name grouped together
        # sorted(zip(param1,param2)) sorts according to param1
        return [p for _, p in sorted(zip(tab_name_list, params_to_be_searched))]

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

    @staticmethod
    def save_to_csv(scrapped_data: dict, name_of_csv: str, path=None):
        """Save scrapped data to a csv file.

        Parameters
        ----------
        scrapped_data : dict
            company_attribute_dict

        name_of_csv : str
            name of the csv file that is wanted to be created

        path : str
            path of the CSV file where it is intended to be saved
        """
        # Extract column names from the inner dictionaries
        column_names = set()
        for value in scrapped_data.values():
            column_names.update(value.keys())

        # Make "Name" as the first column name of the CSV
        column_names = list(column_names)
        try:
            idx = column_names.index("name")
            column_names.insert(0, column_names.pop(idx))
        except ValueError:
            pass

        # Write to CSV
        csv_file_name = name_of_csv+".csv"
        ticker_column = "Ticker"
        column_names.insert(0, ticker_column)
        if not os.path.exists(csv_file_name):
            with open(csv_file_name, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=column_names)
                writer.writeheader()

        with open(csv_file_name, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_names)

            if csvfile.tell() == 0:
                writer.writeheader()

            for key, value in scrapped_data.items():
                row = {ticker_column: key}
                row.update(value)
                writer.writerow(row)

    def __del__(self):
        """Shut down the driver."""
        self.driver_manager.kill_driver()

    def _scrap_ticker_and_company_names(self):
        """Scrap the tickers of the companies on the page."""
        (init_num, final_num, _) = self._get_num_of_rows(
            self.driver_manager.driver
        )
        num_of_companies_on_page = final_num - init_num + 1

        ticker_list = []
        name_list = []
        for row_index in range(num_of_companies_on_page):
            # Get company tickers
            company_ticker = (
                self.driver_manager.driver.find_elements(
                    By.XPATH, f"// *[ @ id = 'row{row_index}jqxGrid'] / div[2] / div")[
                    0].text)
            ticker_list.append(company_ticker)

            # Get company names
            company_name = self.driver_manager.driver.find_elements(
                By.XPATH, f"//*[@id='row{row_index}jqxGrid']/"
                          f"div[1]/div/div/a")[0].text
            name_list.append(company_name)

        # ticker_list, name_list = company_dict_temp.items()
        return ticker_list, name_list

    def _fill_attribute_dict(
            self,
            ticker_list,
            param,
            column_index
    ):
        """Fill the company attribute dict with the corresponding parameters.

        Parameters
        ----------
        company_attr_dict_temp : dict
        ticker_list : list[str]
        num_of_companies_on_page : int
        column_index : int
        """
        (init_num, final_num, _) = self._get_num_of_rows(
            self.driver_manager.driver
        )
        one_parameter_dict_per_page = {ticker: dict() for ticker in ticker_list}
        num_of_companies_on_page = final_num - init_num + 1
        # for ticker, row_index in zip(list(company_attr_dict_temp.keys()), range(num_of_companies_on_page)):
        for ticker, row_index in zip(ticker_list, range(num_of_companies_on_page)):
            # Get parameter values
            parameter_value = self.driver_manager.driver.find_elements(
                By.XPATH,
                f"//*[@id='row{row_index}jqxGrid']/"
                f"div[{int(3 + column_index)}]/div"
            )[0].text
            one_parameter_dict_per_page[ticker][param] = parameter_value
        return one_parameter_dict_per_page

    def _scrap_the_page(self, scrap_params):
        """Integrate filling the company dictionary methods.

        Parameters
        ----------
        scrap_params : list
        """
        # Scrap the tickers
        ticker_list, name_list = self._scrap_ticker_and_company_names()
        company_attr_dict_page = {
            ticker: {"name": name} for ticker, name in zip(ticker_list, name_list)
        }

        # For each parameter to be scrapped, fill the dictionary
        previous_tab_name = None
        for param in scrap_params:
            # Click the corresponding header
            tab_name, column_index = list(MAP_OF_HEADERS[param].items())[0]
            column_index -= 1

            # Check if clicking onto a tab name is required
            previous_tab_name = self._change_tab(previous_tab_name, tab_name)

            # Fill dictionary ticker by ticker
            one_parameter_dict_per_page = self._fill_attribute_dict(
                ticker_list,
                param,
                column_index
            )

            for key in list(one_parameter_dict_per_page.keys()):
                company_attr_dict_page[key].update(one_parameter_dict_per_page[key])

        return company_attr_dict_page

    def _change_tab(self, current_tab_name: str, tab_name: str):
        wait_time = 100
        if current_tab_name != tab_name:
            WebDriverWait(self.driver_manager.driver, wait_time).until(
                ec.element_to_be_clickable(
                    (By.XPATH, f"//*[@id='columns_{tab_name}']/a")
                )
            ).click()

        return tab_name

    def scrap_the_table(self, parameters_to_be_scrapped=None):
        """Scrap the whole table including all tabs and pages in macro-trend.

        Parameters
        ----------
        parameters_to_be_scrapped : list[str]
            user inputted list of parameters to be scrapper

        Returns
        -------
        company_attr_dict : dict
            dictionary of the companies associated with their properties
        """
        if parameters_to_be_scrapped is None:
            # Call GUI to interact with the user
            gui = TableScrapperGUI()
            parameters_to_be_scrapped = gui.run_gui()  # Get desired params from user

        # Sort search parameters for efficient interaction with the website
        scrap_params = self._sort_search_parameters(parameters_to_be_scrapped)

        # Print to CL what is searched
        self.logger.info(f"Search Params = {scrap_params}...")

        # Let scrapping begin
        self.logger.info("SCRAPPING STARTED...")

        # Get number of rows per page and total
        (init_num, final_num, max_num) = self._get_num_of_rows(self.driver_manager.driver)

        tqdm_length = max_num - init_num
        with tqdm(total=tqdm_length) as pbar:
            while final_num != max_num:
                # Scrap the current page
                company_attr_current_page = self._scrap_the_page(scrap_params)
                (init_num, final_num, _) = self._get_num_of_rows(self.driver_manager.driver)
                # Update the progress bar
                pbar.update(int(final_num - init_num + 1))

                # Click on the clickable arrow on the table to progress in the pages
                self._progress_one_page()

                # Save the progress to the CSV file
                self.save_to_csv(company_attr_current_page, "temp")

        self.logger.info("SCRAPPING IS DONE!!!")
        self.logger.info(f"SCRAPPED DATA: {scrap_params} ")

    def _progress_one_page(self):
        WebDriverWait(self.driver_manager.driver, 2).until(
            ec.element_to_be_clickable(
                (
                    By.XPATH,
                    "/html/body/div[1]/div[4]/div[2]/div/div/div/div/div[10]/div/div[4]/div"
                )
            )
        ).click()


def main():
    """Run the TableScrapper.

    Returns
    -------
    scrapped_data : dict
        Dictionary of the table in the given url
    """
    scrapper = TableScrapper()  # Initiate TableScrapper
    scrapper.scrap_the_table()


if __name__ == "__main__":
    main()
