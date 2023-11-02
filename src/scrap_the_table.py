# Import libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from src.utils.Logger import Logger


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
        self.tab_names = [
            "overview", 'descriptive', "dividend", "performance_st", "performance_lt",
            "ratios_income", "ratios_debt", "rev_earnings"]
        self.logger = Logger('LoggerFunctionality', str_logger)

    def _create_driver(self):
        """Set driver settings.

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

    def _get_table_headers(self, driver: webdriver.Chrome):
        """Get headers for each tab. tabs=self.tab_names.

        Parameters
        ----------
        driver : WebDriver object

        Returns
        -------
        header_list : dictionary
            dictionary of tab_names with corresponding headers

        """
        header_list = {}
        for name in self.tab_names:
            temp_list = []
            # Each tab's XPATH has "id" given in the form below:
            # id = "columns_<name_of_the_tab>"
            # e.g. for tab "overview", id='columns_overview'
            # To click a tab object, an XPATH -adress of the tab object- is required
            # e.g. "*[@id='columns_overview']/a" => this is the XPATH for clickable overview tab
            # The command below waits upto 10 secs for the given tab object is clickable
            # Then if it is clickable it clicks on it.
            WebDriverWait(driver, 10).until(
                ec.element_to_be_clickable((By.XPATH, f"//*[@id='columns_{name}']/a"))).click()
            table_headers = driver.find_elements(By.XPATH, "//*[@id='columntablejqxGrid']/div")
            if name == "overview":
                temp_list = [elem.text for elem in table_headers]
            else:
                temp_list = [elem.text for elem in table_headers[2:]]
            header_list[name] = temp_list

        return header_list

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
        (init_num, final_num, max_num) = self._get_num_of_rows(driver)
        company_attr_dict = {}
        header_list = self._get_table_headers(driver)
        with tqdm(total=max_num) as pbar:
            while final_num != max_num:
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
                for name in header_list.keys():
                    # Click the corresponding header
                    WebDriverWait(driver, 10).until(
                        ec.element_to_be_clickable((By.XPATH, f"//*[@id='columns_{name}']/a"))) \
                        .click()

                    if name == "overview":
                        for column_index in range(len(header_list[name]) - 2):
                            for row_index in range(final_num - init_num + 1):
                                com_tck = list(company_attr_dict.keys())[
                                    int(init_num + row_index - 1)]
                                attr = driver.find_elements(
                                    By.XPATH,
                                    f"//*[@id="
                                    f"'row{row_index}jqxGrid']/div[{int(3 + column_index)}]/div")[
                                    0].text
                                company_attr_dict[com_tck][header_list[name][
                                    int(2 + column_index)]] = attr
                    else:
                        for column_index in range(len(header_list[name])):
                            for row_index in range(final_num - init_num + 1):
                                com_tck = list(company_attr_dict.keys())[
                                    int(init_num + row_index - 1)]
                                attr = driver.find_elements(
                                    By.XPATH,
                                    f"//*[@id='row{row_index}jqxGrid']/"
                                    f"div[{int(3 + column_index)}]/div")[
                                    0].text
                                company_attr_dict[com_tck][header_list[name][
                                    int(column_index)]] = attr

                pbar.update(20)
                WebDriverWait(driver, 2).until(ec.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div/div/div[10]/div/"
                               "div[4]/div"))).click()

        self.logger.info("SCRAPPING IS DONE!!!")
        return company_attr_dict


if __name__ == "__main__":
    scrapper = TableScrapper()
    scrapped_data = scrapper.scrap_the_table()
