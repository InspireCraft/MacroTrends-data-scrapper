# Import libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm
from src.utils.Logger import Logger
import json
from src.map_of_headers import MAP_OF_HEADERS
from src.utils.create_driver import create_driver
import os
from src.utils.manage_driver import ManageDriver

#TODO: STATICMETHOD GETNUMBERS
# init_num - final_num + 1 -> variable
# DEF FUNC (
# FORMAT
# )
# for name in search_parameters -> fpr param in ...
# EFFICIENT -> READABLE
# .items() --> get dict elements as tuple
# row'a gel colunmlari al full !!!!
# company name

class TableScrapper:
    """
    Class to be used to scrap the table data in macro-trends.

    Attributes
    ----------
    url : str
        Website url

    tab_names : list of str
        list of the names of the table tabs

    logger : Logger object

    Methods
    -------
    scrap_the_table():
        return the table data in dictionary format

    """

    def __init__(self, url='https://www.macrotrends.net/stocks/stock-screener', str_logger="info"):
        """
        Construct instant variables.

        Parameters
        ----------
        url : str
              the url of the website that is going to be scrapped
        str_logger : str
              the functionality string of the logger object
        """
        self.driver_manager = ManageDriver()  # Initialize driver manager object
        self.driver_manager.set_up_driver(url)  # Set up the driver by using the url
        self.str_logger = str_logger
        self.logger = Logger(self.__class__.__name__, str_logger)

        # Read JSON file for parameters required to be searched
        path_for_search_parameters = os.path.dirname(os.path.abspath(__file__))
        f_search = open(f"{path_for_search_parameters}\\searchParameters.json")
        search_dict = json.load(f_search)
        f_search.close()

        self.search_params = [element for element in search_dict["search_parameters"]]
        self.logger.info(f"Search Params = {self.search_params}...")


    def _get_num_of_rows(self, driver) -> "tuple[int,int,int]":
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
                num_of_elements_on_page = final_num - init_num + 1
                # Construct the dict by scrapping company tickers and add names afterwards
                for row_index in range(num_of_elements_on_page):
                    # Get tickers
                    company_ticker = (
                        self.driver_manager.driver.find_elements(
                            By.XPATH, f"// *[ @ id = 'row{row_index}jqxGrid'] / div[2] / div")[
                            0].text)
                    company_attr_dict[company_ticker] = {}

                    # Get names
                    attr = self.driver_manager.driver.find_elements(
                        By.XPATH, f"//*[@id='row{row_index}jqxGrid']/"
                                  f"div[1]/div/div/a")[0].text
                    company_attr_dict[company_ticker]['name'] = attr

                company_ticker_list = list(company_attr_dict.keys())

                # Fill the dictionary by the keys of the headers
                for name in self.search_params:
                    # Click the corresponding header
                    tab_name = list(MAP_OF_HEADERS[name].keys())[0]
                    WebDriverWait(self.driver_manager.driver, 10).until(
                        ec.element_to_be_clickable((By.XPATH,
                                                    f"//*[@id='columns_{tab_name}']/a"))) \
                        .click()

                    # Retrive the required information after clicking on the corresponding header
                    column_index = list(MAP_OF_HEADERS[name].values())[0] - 1
                    for row_index in range(num_of_elements_on_page):
                        com_tck = company_ticker_list[
                            int(init_num + row_index - 1)]
                        attr = self.driver_manager.driver.find_elements(
                            By.XPATH,
                            f"//*[@id='row{row_index}jqxGrid']/"
                            f"div[{int(3 + column_index)}]/div")[
                            0].text
                        company_attr_dict[com_tck][name] = attr

                # Update the progress bar
                pbar.update(int(num_of_elements_on_page))

                # Click on the clickable arrow on the table to progress in the pages
                WebDriverWait(self.driver_manager.driver, 2).until(ec.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div/div/div[10]/div/"
                               "div[4]/div"))).click()

        self.logger.info("SCRAPPING IS DONE!!!")
        self.logger.info(f"SCRAPPED DATA: {self.search_params} ")

        # Shut down the driver
        self.driver_manager.kill_driver()
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
