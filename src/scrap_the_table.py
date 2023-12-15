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
        self.url = url
        self.str_logger = str_logger
        self.logger = Logger(self.__class__.__name__, str_logger)

        # Read JSON file for parameters required to be searched
        os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__))))
        f_search = open("searchParameters.json")
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
        # Create driver to scrap/interact with the website
        driver = create_driver(self.str_logger)

        # Get the url of the website to be scrapped
        driver.get(self.url)

        # Let scrapping begin
        self.logger.info("SCRAPPING STARTED...")

        # Get number of rows per page and total
        (init_num, final_num, max_num) = self._get_num_of_rows(driver)

        # Initialize attribute dictionary
        company_attr_dict = {}

        # Track the progress of the scrapping process with a progress bar
        with tqdm(total=max_num) as pbar:
            while final_num != max_num:
                (init_num, final_num, _) = self._get_num_of_rows(driver)

                # Construct dict by scrapping company tickers
                for row_index in range(final_num - init_num + 1):
                    company_ticker = (
                        driver.find_elements(
                            By.XPATH, f"// *[ @ id = 'row{row_index}jqxGrid'] / div[2] / div")[
                            0].text)
                    company_attr_dict[company_ticker] = {}

                # Add company names after tickers
                for row_index in range(final_num - init_num + 1):
                    com_tck = list(company_attr_dict.keys())[int(init_num + row_index - 1)]
                    attr = driver.find_elements(
                        By.XPATH, f"//*[@id='row{row_index}jqxGrid']/div[1]/div/div/a")[
                        0].text
                    company_attr_dict[com_tck]['name'] = attr

                # Fill the dictionary by the keys of the headers
                for name in self.search_params:
                    # Click the corresponding header
                    tab_name = list(MAP_OF_HEADERS[name].keys())[0]
                    WebDriverWait(driver, 10).until(
                        ec.element_to_be_clickable((By.XPATH,
                                                    f"//*[@id='columns_{tab_name}']/a"))) \
                        .click()

                    # Retrive the required information after clicking on the corresponding header
                    column_index = list(MAP_OF_HEADERS[name].values())[0] - 1
                    for row_index in range(final_num - init_num + 1):
                        com_tck = list(company_attr_dict.keys())[
                            int(init_num + row_index - 1)]
                        attr = driver.find_elements(
                            By.XPATH,
                            f"//*[@id='row{row_index}jqxGrid']/"
                            f"div[{int(3 + column_index)}]/div")[
                            0].text
                        company_attr_dict[com_tck][name] = attr

                # Update the progress bar
                pbar.update(20)

                # Click on the clickable arrow on the table to progress in the pages
                WebDriverWait(driver, 2).until(ec.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div/div/div[10]/div/"
                               "div[4]/div"))).click()

        self.logger.info("SCRAPPING IS DONE!!!")
        self.logger.info(f"SCRAPPED DATA: {self.search_params} ")

        # Shut down the driver
        driver.close()
        driver.quit()
        return company_attr_dict


def main():
    """Run the TableScrapper.

    Returns
    -------
    scrapped_data : dict
        Dictionary of the table in the given url
    """
    scrapper = TableScrapper()
    scrapped_data = scrapper.scrap_the_table()
    return scrapped_data


if __name__ == "__main__":
    main()
