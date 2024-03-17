# Import libraries
from copy import deepcopy
import csv
import os
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from src.map_of_headers import MAP_OF_HEADERS
from src.utils.Logger import Logger
from src.utils.manage_driver import DriverManager
from src.gui_scrap_the_table import TableScrapperGUI


def merge_unique_with_order(list1, list2):
    # Create a set to keep track of unique elements
    unique_set = set()

    # Create a new list to store merged unique elements in order
    merged_list = []

    # Add elements from list1 to merged_list
    for item in list1:
        # Add item to the merged list if it's not already present
        if item not in unique_set:
            merged_list.append(item)
            unique_set.add(item)

    # Add elements from list2 to merged_list if they are not already present
    for item in list2:
        if item not in unique_set:
            merged_list.append(item)
            unique_set.add(item)

    return merged_list

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
    def save_to_csv(
        scrapped_data: dict[str:dict[str:Any]],
        name_of_csv: str,
        ticker_column_str: str = None
    ):
        """Save scrapped data to a csv file.

        Scrapped data is a dictionary where scrapped parameters of a company is
        stored by using their ticker as an identifer key. CSV file is expected
        to keep the tickers in a column whose name is provided to the function.
        Then, if a company ticker already exist in the provided csv file, the
        corresponding row will be updated. Otherwise, a new row will be appended
        to the end of the file.

        Parameters
        ----------
        scrapped_data : dict
            company_attribute_dict

        name_of_csv : str
            name of the csv file that is wanted to be created

        ticker_column_str : str
            column header name where the ticker values are stored in the csv file
        """
        if ticker_column_str is None:
            ticker_column_str = "Ticker"

        # Extract column names from the dictionaries contained in . These values are the
        # scrapped parameters, which we will be writing to the csv file. Each
        # parameter will be in a separate column.
        column_names_set = {
            ticker_str for company_info_scrapped in scrapped_data.values()
            for ticker_str in company_info_scrapped.keys()
        }  # nested set comprehension (first for: outer)

        # Make ticker column(ticker_column_str) and the company name ("name")
        # first and the second column of the CSV file.
        column_names_input_data = list(column_names_set)
        column_names_input_data = TableScrapper._put_as_first_element(column_names_input_data, "name")
        column_names_input_data.insert(0, ticker_column_str)

        # Write data to CSV
        csv_file_name = name_of_csv if name_of_csv.endswith(".csv") else name_of_csv + ".csv"
        if not os.path.exists(csv_file_name):
            # CSV file does not exist, create one. Create the columns.
            existing_column_names = []
            existing_tickers = []
            with open(csv_file_name, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=column_names_input_data)
                writer.writeheader()
        else:
            # CSV file exists, Read the columns and the company tickers to note
            # which companies already have rows assigned to them in the CSV
            # file.
            with open(csv_file_name, "r") as csvfile:
                reader = csv.reader(csvfile)
                existing_column_names = next(reader)  # read first row to get the headers.

                # Ticker column must already exist, assert that and get the column index
                assert ticker_column_str in existing_column_names, \
                    f"Ticker column provided (={ticker_column_str}) " \
                    "does not exist in the first row of the existing CSV file. " \
                    f"Headers in the file are: ({existing_column_names})"

                try:
                    # Search for the column where the ticker is stored
                    ticker_column_index_in_file = existing_column_names.index(ticker_column_str)
                except ValueError:
                    # We put ticker first if it is up to us, so this is hard-coded for now
                    ticker_column_index_in_file = 0

                # get all the existing tickers in the csv document
                existing_tickers = [row[ticker_column_index_in_file] for row in reader]

        # Stores all the columns names contained in the csv data and the current input
        all_columns = merge_unique_with_order(existing_column_names, column_names_input_data)

        # Split scrapped data into two subdictionaries, first corresponding to
        # the data of the companies which already have a row in the csv file,
        # second corresponding to the data of the companies which do not yet a
        # row in the csv file.
        data_for_existing_tickers = {}
        data_for_new_tickers = {}

        for ticker, company_data_scrapped in scrapped_data.items():
            if ticker in existing_tickers:
                data_for_existing_tickers[ticker] = company_data_scrapped
            else:
                data_for_new_tickers[ticker] = company_data_scrapped

        # For the former part, corresponding row in the csv file will be
        # updated, whereas for the latter part, a new row will be appended to
        # the csv file with all the available information in the scrapped data.
        # Update csv row using the data for existing tickers
        TableScrapper._update_existing_rows(
            csv_file_name,
            ticker_column_str,
            all_columns,
            data_for_existing_tickers,
        )

        TableScrapper._append_rows(
            csv_file_name,
            ticker_column_str,
            all_columns,
            data_for_new_tickers,
        )

    @staticmethod
    def _update_existing_rows(
        csv_file,
        ticker_column_str,
        all_columns,
        data_for_existing_tickers,
    ):
        """Overwrite rows of companies that already contain information in the csv file.

        Args:
        ----
            csv_file (_type_): _description_
            row_index (_type_): _description_
            new_data (_type_): _description_
            all_columns (_type_): _description_
        """
        temp_file = csv_file + ".temp"

        # Write modified rows to temporary file
        with open(csv_file, 'r', newline='') as infile, open(temp_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.DictWriter(outfile, fieldnames=all_columns)
            writer.writeheader()
            for i, row in enumerate(reader):
                if i == 0:
                    # First row contains the headers
                    existing_column_names = deepcopy(row)
                    continue
                # Second row and on (i.e., i >=1 ) contains company data
                row_dict = {key: val for key, val in zip(existing_column_names, row)}
                existing_ticker_str = row_dict[ticker_column_str]

                if existing_ticker_str in data_for_existing_tickers:
                    row_dict.update(data_for_existing_tickers[existing_ticker_str])  # update row
                writer.writerow(row_dict)

        # Replace original file with temporary file
        import os
        os.replace(temp_file, csv_file)

    @staticmethod
    def _append_rows(
        csv_file_name,
        ticker_column_str,
        all_columns,
        data_for_new_tickers: dict[str:Any]
    ):
        """Append rows to the csv for the companies which do not occupy a row in the data yet."""
        with open(csv_file_name, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_columns)

            if csvfile.tell() == 0:
                writer.writeheader()

            for ticker, value in data_for_new_tickers.items():
                row = {ticker_column_str: ticker}
                row.update(value)
                writer.writerow(row)

    @staticmethod
    def _put_as_first_element(input_list: list, value):
        """Put the value in the list as the first element, if the value exist in the list.

        Args:
        ----
            input_list (list): list that (possibly) contains the value
            value (Any): value to be put as the first item in of the list
        """
        try:
            idx = input_list.index(value)
            input_list.insert(0, input_list.pop(idx))
        except ValueError:
            pass
        return input_list

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
