from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

TABS = ["income-statement", "balance-sheet", "cash-flow-statement", "financial-ratios"]


class FinancialDataScraper:
    """Scraps the financial data of companies, which are to be used in the Magic Formula."""

    def __init__(self):
        pass

    @staticmethod
    def scrap_company_financials(ticker: str, name: str, financial_properties: list):
        """Scrap."""
        scrapped_data = dict()
        # Check inputs
        n_properties_to_scrap_total = len(financial_properties)
        if n_properties_to_scrap_total == 0:
            return scrapped_data
        driver = FinancialDataScraper._create_webdriver()

        # For each company, visit each tab and retrieve the data from the financial properties,
        # along with the date information
        for report_name in TABS:
            url_to_visit = FinancialDataScraper._get_fixed_url_pattern(ticker=ticker,
                                                                       name=name,
                                                                       report_name=report_name)
            driver.get(url_to_visit)
            # There is a table in each url,
            # the rows have role and id set to "row"
            # column row have id "columntable", and individual columns have id = "columnheader"
            row_element = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"][id*="row"]')
            first_row = row_element[0]
            child_elements = first_row.find_elements(By.CSS_SELECTOR, 'div')
            for child in child_elements:
                print(child.accessible_name)
            columns = driver.find_elements(By.CSS_SELECTOR, 'div[id*="columntable"]')
            column_headers = columns[0].find_elements(By.CSS_SELECTOR,"div[role=columnheader]")
            for col in column_headers:
                print(col.accessible_name)
            break

        driver.quit()

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
    def _get_fixed_url_pattern(ticker: str, name: str, report_name: str):
        tail = ticker.upper() + "/" + name.lower() + "/" + report_name
        return "https://www.macrotrends.net/stocks/charts/" + tail


if __name__ == "__main__":
    financials_scrapper = FinancialDataScraper()
    scrapped_data = financials_scrapper.scrap_company_financials("AAPL", "apple", ["EBIT"])
