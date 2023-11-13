from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from utils.Logger import Logger
import re
from selenium.webdriver.remote.webelement import WebElement
import pandas as pd

_TABS = ["income-statement", "balance-sheet", "cash-flow-statement", "financial-ratios"]


def _convert_strings_to_floats(element_list: list[WebElement]):
    parsed_floats = [float(re.sub(r'[^\d,]', '', s.accessible_name).replace(',', '.'))
                     if s.accessible_name and re.sub(r'[^\d.]', '', s.accessible_name)
                     else float("nan") for s in element_list]
    return parsed_floats


def _is_not_nan(val: float) -> bool:
    # two nan's are not equal to each other
    return not (val != val)


def _is_date_pattern(element: WebElement):
    # Match[str] is truthy, None is falsy and can be used in filter()
    date_pattern = r"\d{4}-\d{2}-\d{2}"
    return re.match(date_pattern, element.accessible_name)


class FinancialDataScraper:
    """Scraps the financial data of companies, which are to be used in the Magic Formula."""

    def __init__(self, logging_level_str: str = "none"):
        self.logger = Logger("FinancialDataScrapper", logging_level_str)
        self.logger.info("Initialized.")
        self.row_indices = []

    def scrap_company_financials(self, ticker: str, name: str, financial_properties: list):
        """Scrap."""
        scrapped_data = dict()
        # Check inputs
        n_properties_to_scrap_total = len(financial_properties)
        if n_properties_to_scrap_total == 0:
            return scrapped_data
        n_properties_to_scrap_current = n_properties_to_scrap_total
        driver = FinancialDataScraper._create_webdriver()

        # For each company, visit each tab and retrieve the data from the financial properties,
        # along with the date information
        for report_name in _TABS:
            self.logger.debug("Searching through '" + report_name + "'...")
            # There is a table in each url,
            url_to_visit = FinancialDataScraper._get_fixed_url_pattern(ticker=ticker,
                                                                       name=name,
                                                                       report_name=report_name)
            self.logger.debug("Accessing " + url_to_visit + "...")
            driver.get(url_to_visit)
            # the column row has id "columntable", and individual columns have id = "columnheader"
            columns = driver.find_elements(By.CSS_SELECTOR, 'div[id*="columntable"]')
            column_headers = columns[0].find_elements(By.CSS_SELECTOR, "div[role=columnheader]")
            dates_of_columns = [web_element.accessible_name for web_element in
                                filter(_is_date_pattern, column_headers)]

            # the rows have role and id set to "row"
            row_element = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"][id*="row"]')
            for row in row_element:
                child_elements = row.find_elements(By.CSS_SELECTOR, 'div')
                financial_property_name = child_elements[0].accessible_name
                if financial_property_name in financial_properties:
                    self.logger.debug(
                        "Found '" + financial_property_name + "' in '" + report_name + "'.")
                    # Convert the WebElements.accessible_name to float representation
                    accesible_names_float = _convert_strings_to_floats(child_elements[1:])

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
                    df = pd.DataFrame({'Date': dates_of_columns,
                                       financial_property_name: valid_float_values})

                    # Key is the financial property itself
                    scrapped_data[financial_property_name] = df

                    n_properties_to_scrap_current -= 1
            if n_properties_to_scrap_current == 0:
                self.logger.info("Scrapping is successful, every requested field is scrapped!")
                break
        if n_properties_to_scrap_current > 0:
            financial_properties_not_found = [
                item for item in financial_properties if item not in scrapped_data.keys()]
            self.logger.warning("Following financial properties are not found:")
            self.logger.warning(financial_properties_not_found)

        driver.quit()
        return scrapped_data

    @staticmethod
    def _create_webdriver() -> webdriver.Chrome:
        options = Options()
        # Run Selenium without opening an actual browser
        options.add_argument("--headless")
        # options.add_argument("--enable-webgl")
        options.add_argument("--use-gl=angle")
        options.add_argument("--use-angle=swiftshader")
        return webdriver.Chrome(options=options)

    @staticmethod
    def _parse_numeric_value(value: str) -> float:
        try:
            print("Value is " + value)
            return float(re.sub(r'[^\d,]', '', value))
        except ValueError:
            return float("nan")

    @staticmethod
    def _get_fixed_url_pattern(ticker: str, name: str, report_name: str):
        tail = ticker.upper() + "/" + name.lower() + "/" + report_name
        return "https://www.macrotrends.net/stocks/charts/" + tail


if __name__ == "__main__":
    financials_scrapper = FinancialDataScraper("debug")
    scrapped_data = financials_scrapper.scrap_company_financials(
        "AAPL", "apple", ["EBIT", "Total Current Assets", "Invalid-Field"])
    print(scrapped_data)
