# Import libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm


class ScrapTable:
    def __init__(self, driver):
        self.driver = driver
        self.tab_names = ["overview", 'descriptive', "dividend", "performance_st", "performance_lt",
                     "ratios_income", "ratios_debt", "rev_earnings"]

    def get_table_headers(self):
        # Get headers for each tab. tabs=[overview, descriptive, dividends, ..., revenue&earnings]
        header_list = {}
        for name in self.tab_names:
            temp_list = []
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//*[@id='columns_{name}']/a"))).click()
            table_headers = self.driver.find_elements(By.XPATH, "//*[@id='columntablejqxGrid']/div")
            if name == "overview":
                temp_list = [elem.text for elem in table_headers]
            else:
                temp_list = [elem.text for elem in table_headers[2:]]
            header_list[name] = temp_list

        return header_list

    def get_page_numbers_in_table(self):
        # get 1-20 of X items
        temp = self.driver.find_elements(By.XPATH, "// *[ @ id = 'pagerjqxGrid'] / div / div[6]")
        current_intial_number = temp[0].text.split("-")[0]
        current_final_number = temp[0].text.split("-")[1].split(" ")[0]
        number_of_item_in_the_list = temp[0].text.split("-")[1].split(" ")[2]
        return current_intial_number, current_final_number, number_of_item_in_the_list

    def scrap_the_table(self):
        '''
        Read the table in the given url.
        Scrapping is performed row-by-row.
        After scrapping a row, another table header is clicked and scrapping the same row continous.
        '''
        (init_num, final_num, max_num) = self.get_page_numbers_in_table()
        company_attr_dict = {}
        header_list = self.get_table_headers()
        with tqdm(total=int(max_num)) as pbar:
            while int(final_num) != int(max_num):
                (init_num, final_num, _) = self.get_page_numbers_in_table()
                for row_index in range(int(int(final_num) - int(init_num)) + 1):
                    company_name = (
                        self.driver.find_elements(By.XPATH, f"//*[@id='row{row_index}jqxGrid']/div[1]/div/div/a")[0].text)
                    company_attr_dict[company_name] = {}
                    for name in header_list.keys():
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, f"//*[@id='columns_{name}']/a"))).click()
                        if name == "overview":
                            for column_index in range(len(header_list[name]) - 2):
                                temp = self.driver.find_elements(By.XPATH,
                                                            f"//*[@id='row{row_index}jqxGrid']/div[{int(3 + column_index)}]/div")[
                                    0].text
                                company_attr_dict[company_name][header_list[name][int(2 + column_index)]] = temp
                        else:
                            for column_index in range(len(header_list[name])):
                                temp = self.driver.find_elements(By.XPATH,
                                                            f"//*[@id='row{row_index}jqxGrid']/div[{int(3 + column_index)}]/div")[
                                    0].text
                                company_attr_dict[company_name][header_list[name][int(column_index)]] = temp
                    pbar.update(1)
                WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div/div/div[10]/div/div[4]/div"))).click()
        return company_attr_dict


    def scrap_the_table_fast(self):
        '''
        Read the table in the given url.
        Scrapping is performed row-by-row.
        After scrapping a row, another table header is clicked and scrapping the same row continous.
        '''
        print('SCRAPPING STARTED')
        (init_num, final_num, max_num) = self.get_page_numbers_in_table()
        company_attr_dict = {}
        header_list = self.get_table_headers()
        with tqdm(total=int(max_num)) as pbar:
            while int(final_num) != int(max_num):
                (init_num, final_num, _) = self.get_page_numbers_in_table()

                # Construct dict by creating company tickers
                for row_index in range(int(int(final_num) - int(init_num)) + 1):
                    company_ticker = (
                        self.driver.find_elements(By.XPATH, f"// *[ @ id = 'row{row_index}jqxGrid'] / div[2] / div")[
                            0].text)
                    company_attr_dict[company_ticker] = {}

                for row_index in range(int(int(final_num) - int(init_num)) + 1):
                    com_tck = list(company_attr_dict.keys())[int(int(init_num) + row_index - 1)]
                    attr = self.driver.find_elements(By.XPATH,
                                                     f"//*[@id='row{row_index}jqxGrid']/div[1]/div/div/a")[
                        0].text
                    company_attr_dict[com_tck]['name'] = attr

                # Fill the dictionary by the keys of the headers
                for name in header_list.keys():
                    # Click the corresponding header
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//*[@id='columns_{name}']/a"))).click()

                    if name == "overview":
                        for column_index in range(len(header_list[name]) - 2):
                            for row_index in range(int(int(final_num) - int(init_num)) + 1):
                                com_tck = list(company_attr_dict.keys())[int(int(init_num)+row_index-1)]
                                attr = self.driver.find_elements(By.XPATH,
                                                            f"//*[@id='row{row_index}jqxGrid']/div[{int(3 + column_index)}]/div")[
                                    0].text
                                company_attr_dict[com_tck][header_list[name][int(2 + column_index)]] = attr
                    else:
                        for column_index in range(len(header_list[name])):
                            for row_index in range(int(int(final_num) - int(init_num)) + 1):
                                com_tck = list(company_attr_dict.keys())[int(int(init_num)+row_index-1)]
                                attr = self.driver.find_elements(By.XPATH,
                                                                 f"//*[@id='row{row_index}jqxGrid']/div[{int(3 + column_index)}]/div")[
                                    0].text
                                company_attr_dict[com_tck][header_list[name][int(column_index)]] = attr

                pbar.update(20)
                WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div/div/div[10]/div/div[4]/div"))).click()
        return company_attr_dict






# def get_company_names(driver):
#     company_names = []
#     (init_num, final_num, max_num) = get_page_numbers_in_table(driver)
#     cnt = 0
#     company_names = []
#     with tqdm(total=int(max_num)) as pbar:
#         while int(final_num) != int(max_num):
#             (init_num, final_num, _) = get_page_numbers_in_table(driver)
#             for row_index in range(int(int(final_num)-int(init_num))+1):
#                 company_names.append(driver.find_elements(By.XPATH, f"//*[@id='row{row_index}jqxGrid']/div[1]/div/div/a")[0].text)
#             pbar.update(len(company_names))
#             WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div/div/div/div[10]/div/div[4]/div"))).click()
#     return company_names