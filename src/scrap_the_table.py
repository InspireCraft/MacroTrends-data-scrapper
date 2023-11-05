# Import libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from src.utils.Logger import Logger
import json
from src.map_of_headers import map_of_headers

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
        self.logger = Logger(self.__class__.__name__, str_logger)

        f_search = open("../src/config2.json")
        search_dict = json.load(f_search)
        f_search.close()
        self.search_params = [elem for elem in search_dict["search_parameters"]]

        # f = open("../src/config.json")
        # config = json.load(f)
        # f.close()
        # self.tab_names = [elem for elem in config["tab_names"].keys()]

        self.logger.info(f"Search Params = {self.search_params}...")

    def _create_driver(self) -> "webdriver.chrome":
        """Create driver object.

        Driver is an WebDriver object that interacts with the website. Clicking,
        reading are the methods of the driver object.

        Parameters
        ----------
        None

        Returns
        -------
        driver : WebDriver object

        """
        self.logger.info("WebDriver is being created...")
        options = Options()
        options.add_argument("--headless")  # Run selenium without opening an actual browser

        driver = webdriver.Chrome(options=options)  # Initialize the driver instance
        driver.get(self.url)
        self.logger.info("WebDriver is created!!!")
        return driver

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
        driver = self._create_driver()
        self.logger.info("SCRAPPING STARTED...")
        ###
        # FILTERING CAN BE INTEGRATED HERE
        ###
        (init_num, final_num, max_num) = self._get_num_of_rows(driver)
        company_attr_dict = {}
        CNT = 0
        with tqdm(total=max_num) as pbar:
            while final_num != max_num and CNT<2:
                (init_num, final_num, _) = self._get_num_of_rows(driver)

                # Construct dict by creating company tickers
                for row_index in range(final_num - init_num + 1):
                    company_ticker = (
                        driver.find_elements(
                            By.XPATH, f"// *[ @ id = 'row{row_index}jqxGrid'] / div[2] / div")[
                            0].text)
                    company_attr_dict[company_ticker] = {}

                for row_index in range(final_num - init_num + 1):
                    com_tck = list(company_attr_dict.keys())[int(init_num + row_index - 1)]
                    attr = driver.find_elements(
                        By.XPATH, f"//*[@id='row{row_index}jqxGrid']/div[1]/div/div/a")[
                        0].text
                    company_attr_dict[com_tck]['name'] = attr

                # Fill the dictionary by the keys of the headers
                for name in self.search_params:
                    # Click the corresponding header
                    tab_name = list(map_of_headers[name].keys())[0]
                    WebDriverWait(driver, 10).until(
                        ec.element_to_be_clickable((By.XPATH, f"//*[@id='columns_{tab_name}']/a"))) \
                        .click()
                    self.logger.info(f"Clicked on {tab_name}...")

                    for row_index in range(final_num - init_num + 1):
                        column_index = list(map_of_headers[name].values())[0]-1
                        com_tck = list(company_attr_dict.keys())[
                            int(init_num + row_index - 1)]
                        attr = driver.find_elements(
                            By.XPATH,
                            f"//*[@id='row{row_index}jqxGrid']/"
                            f"div[{int(3 + column_index)}]/div")[
                            0].text
                        company_attr_dict[com_tck][name] = attr

                pbar.update(20)
                CNT += 1
                # break
                WebDriverWait(driver, 2).until(ec.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div/div/div[10]/div/"
                               "div[4]/div"))).click()

        self.logger.info("SCRAPPING IS DONE!!!")
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
    import csv

    my_dict = scrapped_data

    with open('try_selective_scrap.csv', 'w') as f:  # You will need 'wb' mode in Python 2.x
        w = csv.DictWriter(f, my_dict.keys())
        w.writeheader()
        w.writerow(my_dict)
    return scrapped_data


if __name__ == "__main__":
    main()
