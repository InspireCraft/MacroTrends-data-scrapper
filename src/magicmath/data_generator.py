import pandas as pd
import random
from typing import List, Union, Dict


class DataFrameGenerator:
    """
    Generate pandas DataFrames with specified column names, row size, and randomization method.

    Raises
    ------
    ValueError
        If an invalid randomization method is provided.

    Examples
    --------
    To generate a DataFrame with 5 rows and random data:

    >>> generator = DataFrameGenerator()
    >>> df = generator.generate_dataframe(["A", "B", "C"], 5, randomization_method="random")
    >>> print(df)
    """

    def __init__(self):
        pass

    def generate_dataframe(self, column_names: List[str], row_size: int,
                           randomization_method: str = "random") -> pd.DataFrame:
        """
        Generate a pandas DataFrame based on the specified randomization method.

        Parameters
        ----------
        column_names : List[str]
            List of column names for the DataFrame.
        row_size : int
            Number of rows in the DataFrame.
        randomization_method : str, optional
            Randomization method for data generation. Options: "random" or "zeros".

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame with randomized data.
        """
        self._set_data_generation_params(column_names, row_size, randomization_method)
        data = self._generate_data()
        return pd.DataFrame(data, columns=self.column_names)

    def _set_data_generation_params(self, column_names: List[str], row_size: int,
                                    randomization_method: str = "random"):
        self.column_names = column_names
        self.row_size = row_size
        self.randomization_method = randomization_method

    def _generate_data(self) -> Dict[str, List[Union[float, int]]]:
        if self.randomization_method == "random":
            data = self._generate_random_data()
        elif self.randomization_method == "zeros":
            data = self._generate_zeros_data()
        else:
            raise ValueError("Invalid randomization method")

        return data

    def _generate_random_data(self) -> Dict[str, List[float]]:
        data = {col: [random.uniform(0, 1) for _ in range(self.row_size)]
                for col in self.column_names}
        return data

    def _generate_zeros_data(self) -> Dict[str, List[int]]:
        data = {col: [0] * self.row_size for col in self.column_names}
        return data


# Example usage:
if __name__ == "__main__":
    column_names = ["A", "B", "C"]
    row_size = 5
    randomization_method = "random"  # You can change this to "zeros" or any other method

    generator = DataFrameGenerator()
    df = generator.generate_dataframe(column_names, row_size, randomization_method)
    print(df)
