# MacroTrend data scrapper

Package for scrapping the desired data from the [MacroTrend stocks screner](https://www.macrotrends.net/stocks/stock-screener) and saving it into a `.csv` file.

![alt text](readme_images/tableExplainer.png)

An example of the scrapped data in a `.csv` file is given below.

![alt text](readme_images/excel.PNG)

First column and the second column of the `.csv` are always
set to `Ticker` and `name`, respectively.

## Installation

### Prerequisites

- Python 3.x is installed to your system

### Installation steps

1. Clone this repository to your local machine

   ```bash
   git clone git@github.com:AlpSari/MagicInvest.git
   ```

2. Go to the directory

   ```bash
   cd MagicInvest
   ```

3. (Optional) Create a Python virtual environment and activate it:

   ```bash
   python -m venv .venv/
   ```

   From Windows command prompt (i.e., cmd), activate the virtual environment by:

   ```bash
   .venv/Scripts/activate
   ```

4. Install the required dependencies using pip:
   
   ```bash
   pip install -r requirements.txt
   ```


### Running the data scrapper

To run the data scrapper:

```bash
python main.py
```

#### Arguments of main.py

- `
--parameters-path
`
 :Input of this argument is the path to the JSON file 
which stores the parameters to be scrapped. 
User can avoid using the GUI by creating a JSON file 
(storing parameters to be scrapped) and providing 
its path via command line. 

   Format of the JSON file:

   ```json
   ["param1", "param2", "...", "paramN"]
   ```

- `
--output-csv
`
 :Input of this argument is the name of the csv file in which
scrapped parameters to be saved. Default name of csv = `output.csv`

- `
--logging-level
`
:Input of this argument controls the logging level of Logger object. 
The valid arguments are ["none", "info", "debug"]. Default level = `none`


Example usage with the arguments:

```bash
python main.py --parameters-path this/is/my/path.JSON --output-csv my_file.csv --logging-level none
```
## Note To Developers

Developers should use the same code checking tools that are being used by the GitHub actions. Those are automatically configured using configuration files in the repository and all the tools and plugins can be downloaded using:

```bash
pip install -r dev_requirements.txt
```

## Testing

Unit tests for the package are available in the `tests/` directory. To run the tests, use the following command:

```bash
python -m unittest discover -v tests
```

Note that some of the GUI-related tests are causing display errors(in remote server); therefore, they are not implemented yet.
