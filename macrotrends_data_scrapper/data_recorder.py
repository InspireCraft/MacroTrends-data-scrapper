import csv
from copy import deepcopy
from typing import Any
import os


class DataRecorder():
    """Updates a CSV file with the recorded data.

    Attributes
    ----------
    csv_file_name : str
        path to the csv file where the data will be stored.
    _is_file_exist: bool
        flag that checks whether the csv_file exists. Only get method for this
        attribute is permitted.
    headers_in_file : list
        headers contained in the first row of the csv file. It is stored as a
        state to reduce I/O operations on the csv file.
    tickers_in_file : list
        Tickers already contained in the csv file. It is stored as a state to
        reduce I/O operations on the csv file.
    """

    def __init__(self, csv_file_name: str):
        self.csv_file_name = csv_file_name \
            if csv_file_name.endswith(".csv") else csv_file_name + ".csv"

        self.headers_in_file = self._extract_headers_from_csv(self.csv_file_name) \
            if self._is_file_exist else None

        self.tickers_in_file = None

    @property
    def _is_file_exist(self):
        pass

    @_is_file_exist.getter
    def _is_file_exist(self) -> bool:
        return os.path.exists(self.csv_file_name)

    def save_to_csv(self, scrapped_data: dict[str:dict[str:Any]], ticker_column_str: str = None):
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
            dictionary where keys are tickers, values are another dictionary
            with key contain the name of the scrapped parameter and the value
            containing the value of the scrapped parameter. Example is
            scrapped_data = {"AAPL": {"MarketCap":100}}

        name_of_csv : str
            name of the csv file to store the scrapped data. It will be modified
            if exists, otherwise created. Note that first row of the csv should
            be reserved for the headers corresponding to the scrapped
            parameters.

        ticker_column_str : str
            String of the column where the ticker values are stored in the csv
            file. It must be one of the values in the first row, if csv file exists.
        """
        if ticker_column_str is None:
            ticker_column_str = "Ticker"

        column_names_input_data = self._extract_parameter_names_from_scrap_data(
            scrapped_data,
            ticker_column_str
        )

        # Write data to CSV
        if not self._is_file_exist:
            # CSV file does not exist, create one. Create the columns.
            with open(self.csv_file_name, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=column_names_input_data)
                writer.writeheader()
            self.headers_in_file = column_names_input_data  # column names are set from the input
            self.tickers_in_file = []  # no ticker exist in the empty csv, list is empty

        else:
            # CSV file exists, Read the columns and the company tickers to note
            # which companies already have rows assigned to them in the CSV
            # file.
            assert ticker_column_str in self.headers_in_file, \
                f"Ticker column provided (={ticker_column_str}) " \
                "does not exist in the first row of the existing CSV file. " \
                f"Headers in the file are: ({self.headers_in_file})"

            if self.tickers_in_file is None:
                # Ticker column must already exist, assert that and get the column index
                ticker_column_index_in_file = self.headers_in_file.index(ticker_column_str)
                # get all the existing tickers in the csv document
                self.tickers_in_file = self._extract_column_with_index_from_csv(
                    self.csv_file_name,
                    ticker_column_index_in_file
                )
            else:
                # self.tickers_in_file is already set here, It cannot be None or an empty list now.
                assert len(self.tickers_in_file) != 0, \
                    f"Tickers in the memory has been initialized already, but has length 0. "\
                    f"Current value is = {self.tickers_in_file}"

        # Split scrapped data into two subdictionaries, first corresponding to
        # the data of the companies which already have a row in the csv file,
        # second corresponding to the data of the companies which do not yet a
        # row in the csv file.
        data_for_existing_tickers = {}
        data_for_new_tickers = {}

        for ticker, company_data_scrapped in scrapped_data.items():
            if ticker in self.tickers_in_file:
                data_for_existing_tickers[ticker] = company_data_scrapped
            else:
                data_for_new_tickers[ticker] = company_data_scrapped

        # Update header & ticker information with the current input
        self.headers_in_file = _merge_unique_with_order(
            self.headers_in_file,
            column_names_input_data
        )
        ticker_names_input_data = list(scrapped_data.keys())
        self.tickers_in_file = _merge_unique_with_order(
            self.tickers_in_file,
            ticker_names_input_data
        )

        # For the former part, corresponding row in the csv file will be
        # updated, whereas for the latter part, a new row will be appended to
        # the csv file with all the available information in the scrapped data.
        # Update csv row using the data for existing tickers
        self._update_existing_rows(
            self.csv_file_name,
            ticker_column_str,
            self.headers_in_file,
            data_for_existing_tickers,
        )

        self._append_rows(
            self.csv_file_name,
            ticker_column_str,
            self.headers_in_file,
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
    def _extract_headers_from_csv(csv_file_path) -> list[str]:
        with open(csv_file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            csv_headers = next(reader)  # read first row to get the headers.
            return csv_headers

    @staticmethod
    def _extract_column_with_index_from_csv(csv_file_path, column_index: int) -> list[str]:
        with open(csv_file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # read first row to skip the headers.
            # Get the element in the specified column from each row
            return [row[column_index] for row in reader]

    @staticmethod
    def _extract_parameter_names_from_scrap_data(
        scrapped_data: dict[str:dict[str:Any]],
        ticker_column_str: str
    ) -> list:
        """Get the scrapped parameters (just names) from the input data, and append a ticker column.

        NOTE: Additionally, The parameters containing the company name (="name")
        is put as the second item.
        """
        # Extract column names from the dictionaries contained in. These values are the
        # scrapped parameters, which we will be writing to the csv file. Each
        # parameter will be in a separate column.
        column_names_set = {
            ticker_str for company_info_scrapped in scrapped_data.values()
            for ticker_str in company_info_scrapped.keys()
        }  # nested set comprehension (first for: outer)

        # Make ticker column(ticker_column_str) and the company name ("name")
        # first and the second column of the CSV file.
        column_names_input_data = list(column_names_set)
        column_names_input_data = _put_as_first_element(column_names_input_data, "name")
        column_names_input_data.insert(0, ticker_column_str)

        return column_names_input_data


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


def _merge_unique_with_order(list1, list2):
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
