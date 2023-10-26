# Import libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


class TableScrapper:
    """
    Class to be used to scrap the table data in macro-trends.

    Attributes
    ----------
    url : str
        Website

    tab_names : list of str
        list of the names of the table tabs

    Methods
    -------
    _set_driver():
        return the WebDriver object

    _get_table_headers(driver):
        return the headers corresponding to each tab

    _get_num_of_items(driver):
        return the (current_item_number,max_item_number_in_that_page,total_num_of_items)

    _scrap_the_table():
        return the table data in dictionary format

    """

    def __init__(self, url='https://www.macrotrends.net/stocks/stock-screener'):
        """
        Construct necessary parameters.

        Parameters
        ----------
        url : str
            website

        tab_names: list of str
            list of the names of the table tabs

        """
        self.url = url
        self.tab_names = [
            "overview", 'descriptive', "dividend", "performance_st", "performance_lt",
            "ratios_income", "ratios_debt", "rev_earnings"]

    def _set_driver(self):
        """
        Set driver settings.

        Parameters
        ----------

        Returns
        -------
        driver : obj
            WebDriver object
        """
        print('Driver is being set...')
        options = Options()
        options.add_argument("--headless")  # Run selenium without opening an actual browser

        driver = webdriver.Chrome(options=options)  # Initialize the driver instance
        driver.get(self.url)
        print('Driver is set!!!')
        return driver

    def _get_table_headers(self, driver):
        """
        Get headers for each tab. tabs=[overview, descriptive, dividends, ..., revenue&earnings].

        Parameters
        ----------
        driver : obj
            WebDriver object

        Returns
        -------
        header_list : dictionary
            dictionary of tab_names with corresponding headers

        """
        header_list = {}
        for name in self.tab_names:
            temp_list = []
            WebDriverWait(driver, 10).until(
                ec.element_to_be_clickable((By.XPATH, f"//*[@id='columns_{name}']/a"))).click()
            table_headers = driver.find_elements(By.XPATH, "//*[@id='columntablejqxGrid']/div")
            if name == "overview":
                temp_list = [elem.text for elem in table_headers]
            else:
                temp_list = [elem.text for elem in table_headers[2:]]
            header_list[name] = temp_list

        return header_list

    def _get_num_of_items(self, driver):
        """
        Check current item number, max item number in current page, total item number.

        Parameters
        ----------
        driver : obj
            WebDriver object

        Returns
        -------
        current_initial_number, current_final_number, number_of_item_in_the_list : tuple of ints

        """
        temp = driver.find_elements(By.XPATH, "// *[ @ id = 'pagerjqxGrid'] / div / div[6]")
        current_initial_number = int(temp[0].text.split("-")[0])
        current_final_number = int(temp[0].text.split("-")[1].split(" ")[0])
        number_of_item_in_the_list = int(temp[0].text.split("-")[1].split(" ")[2])
        return current_initial_number, current_final_number, number_of_item_in_the_list

    def scrap_the_table(self):
        """
        Scraps the whole table including all tabs and pages in macro-trend.

        Parameters
        ----------
        None

        Returns
        -------
        company_attr_dict : dictionary
            dictionary of the companies associated with their properties
        """
        driver = self._set_driver()
        print('SCRAPPING STARTED...')
        (init_num, final_num, max_num) = self._get_num_of_items()
        company_attr_dict = {}
        header_list = self._get_table_headers()
        with tqdm(total=max_num) as pbar:
            while final_num != max_num:
                (init_num, final_num, _) = self._get_num_of_items()

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
        return company_attr_dict
