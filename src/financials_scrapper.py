from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from utils.Logger import Logger
from functools import reduce
import re
from pandas import DataFrame, merge


def _is_not_nan(val: float) -> bool:
    # two nan's are not equal to each other
    return not (val != val)


def _zip_strict(*args):
    """Only uses zip() on args if they have the same length, errors otherwise."""
    arg_lens = [len(arg) for arg in args]
    if len(set(arg_lens)) != 1:
        raise ValueError("All input iterables must have the same length")
    return zip(*args)


def _get_fixed_url_pattern(ticker: str, name: str, report_name: str) -> str:
    tail = ticker.upper() + "/" + name.lower() + "/" + report_name
    return "https://www.macrotrends.net/stocks/charts/" + tail


class FinancialDataScraper:
    """Scraps the financial data of companies, which are to be used in the Magic Formula."""

    _TABS = ["income-statement", "balance-sheet", "cash-flow-statement", "financial-ratios"]

    def __init__(self, logging_level_str: str = "none"):
        self.logger = Logger("FinancialDataScrapper", logging_level_str)
        self.logger.info("Initialized.")
        self.row_indices = []
        self.driver = FinancialDataScraper._create_webdriver()

    def scrap_financials(self,
                         ticker_list: list[str],
                         company_name_list: list[str],
                         financial_properties: list
                         ) -> dict:
        """
        Scrap company financials for each company given in the list.

        Parameters
        ----------
            ticker_list(list[str]): ticker symbol of the company
            company_name_list (list[str]): name of the company
            financial_properties (list): financial instruments to be scrapped, correspond to first
            column of the rows

        Returns
        -------
            dict: dictionary storing  scrapped financial properties in a DataFrame for each company,
            where the company information is stored using the ticker symbol as the keys
        """
        financial_data_dict = {
            ticker: self._scrap_company_financials(ticker, company_name, financial_properties)
            for ticker, company_name in _zip_strict(ticker_list, company_name_list)}
        return financial_data_dict

    def _scrap_company_financials(self,
                                  ticker: str,
                                  company_name: str,
                                  financial_properties: list
                                  ) -> DataFrame:
        """Scrap a single company data and put it on a DataFrame."""
        scrapped_data = dict()
        # Check inputs
        n_properties_to_scrap_total = len(financial_properties)
        if n_properties_to_scrap_total == 0:
            return scrapped_data
        n_properties_to_scrap_current = n_properties_to_scrap_total

        logger_company_header = "[" + company_name + "] "
        # For each company, visit each tab and retrieve the data from the financial properties,
        # along with the date information
        for report_name in self._TABS:
            self.logger.debug(logger_company_header + "Searching through '" + report_name + "'...")
            # There is a table in each url,
            url_to_visit = _get_fixed_url_pattern(ticker=ticker,
                                                  name=company_name,
                                                  report_name=report_name)
            self.logger.debug(logger_company_header + "Accessing " + url_to_visit + "...")
            self.driver.get(url_to_visit)
            # the column row has id "columntable", and individual columns have id = "columnheader"
            columns = self.driver.find_elements(By.CSS_SELECTOR, 'div[id*="columntable"]')
            column_headers = columns[0].find_elements(By.CSS_SELECTOR, "div[role=columnheader]")
            dates_of_columns = [web_element.accessible_name for web_element in
                                filter(self._is_date_pattern, column_headers)]

            # the rows have role and id set to "row"
            row_element = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="row"][id*="row"]')
            for row in row_element:
                child_elements = row.find_elements(By.CSS_SELECTOR, 'div')
                financial_property_name = child_elements[0].accessible_name
                if financial_property_name in financial_properties:
                    logger_msg = "Found '" + financial_property_name + "' in '" + report_name + "'."
                    self.logger.debug(logger_company_header + logger_msg)
                    # Convert the WebElements.accessible_name to float representation
                    accesible_names_float = self._convert_strings_to_floats(child_elements[1:])

                    # For each financial_property we would get the same indices,
                    # so calculate and store it in self.row_indices
                    # TODO: self.row_indices makes sense if this class is re-used
                    # for additional scrapping, otherwise it can be a local variable.
                    # It should be checked if self.row_indices can be used when
                    # scrapping different company financial data.
                    if len(self.row_indices) == 0:
                        valid_float_indices = [idx for (idx, val) in
                                               enumerate(accesible_names_float)
                                               if _is_not_nan(val)]
                        valid_float_values = filter(_is_not_nan, accesible_names_float)
                        self.row_indices = valid_float_indices
                    else:
                        valid_float_values = [accesible_names_float[valid_idx]
                                              for valid_idx in self.row_indices]
                    # Create a Dataframe object
                    df = DataFrame({'Date': dates_of_columns,
                                    financial_property_name: valid_float_values})

                    # Key is the financial property itself
                    scrapped_data[financial_property_name] = df

                    # Reduce the counter and check if all of the required elements are gathered
                    n_properties_to_scrap_current -= 1
                    if n_properties_to_scrap_current == 0:
                        break

            if n_properties_to_scrap_current == 0:
                logger_msg = "Scrapping is successful, every requested field is scrapped!"
                self.logger.info(logger_company_header + logger_msg)
                break

        if n_properties_to_scrap_current > 0:
            financial_properties_not_found = [
                item for item in financial_properties if item not in scrapped_data.keys()]
            logger_msg = "Following financial properties are not found:"
            self.logger.debug(logger_company_header + logger_msg)
            self.logger.debug(financial_properties_not_found)
            if n_properties_to_scrap_current == n_properties_to_scrap_total:
                return DataFrame()

        company_dataframe = reduce(lambda left, right: merge(left, right, on='Date'),
                                   list(scrapped_data.values()))
        return company_dataframe

    def __del__(self):
        """Close browser when the object is deleted."""
        self.driver.quit()

    @staticmethod
    def _convert_strings_to_floats(element_list: list[WebElement]):
        parsed_floats = [float(re.sub(r'[^\d,]', '', s.accessible_name).replace(',', '.'))
                         if s.accessible_name and re.sub(r'[^\d.]', '', s.accessible_name)
                         else float("nan") for s in element_list]
        return parsed_floats

    @staticmethod
    def _is_date_pattern(element: WebElement):
        # Match[str] is truthy, None is falsy and can be used in filter()
        date_pattern = r"\d{4}-\d{2}-\d{2}"
        return re.match(date_pattern, element.accessible_name)

    @staticmethod
    def _create_webdriver() -> webdriver.Chrome:
        options = Options()
        # Run Selenium without opening an actual browser
        options.add_argument("--headless")
        # options.add_argument("--enable-webgl")
        options.add_argument("--use-gl=angle")
        options.add_argument("--use-angle=swiftshader")
        return webdriver.Chrome(options=options)


if __name__ == "__main__":
    financials_scrapper = FinancialDataScraper("debug")
    scrapped_data = financials_scrapper.scrap_financials(
        ["AAPL", "MSFT"],
        ["apple", "microsoft"],
        ["EBIT", "Total Current Assets", "Invalid-Field"])
    print(scrapped_data)
