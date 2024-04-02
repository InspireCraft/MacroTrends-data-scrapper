import argparse
import json
import os

from src.scrap_the_table import TableScrapper


def main():
    """Run the application based on the provided arguments."""
    parser = argparse.ArgumentParser(description="Scrape table data from macro-trends.net")
    parser.add_argument(
        "--parameters-path",
        dest="params_path",
        type=str,
        help="Path to the JSON file where the parameters to be scrapped is listed."
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="Output.csv",
        help="Name of the output CSV file"
    )
    parser.add_argument(
        '--logging-level',
        dest='logger_level',
        metavar='LOGGING_LEVEL_STRING',
        help='Logging level of the game, one of ["none", "info", "debug"]',
        default="none",
        choices=["none", "info", "debug"],
    )

    args = parser.parse_args()

    if args.params_path:
        parameters_to_be_scrapped = _read_strings_from_json(args.params_path)
    else:
        parameters_to_be_scrapped = None

    scrapper = TableScrapper(str_logger=args.logger_level)
    scrapper.scrap_the_table(
        parameters_to_be_scrapped=parameters_to_be_scrapped,
        csv_file=args.output_csv,
    )


def _read_strings_from_json(json_file):
    """Read a list of strings from a JSON file."""
    with open(_create_absolute_file_path(json_file), 'r') as file:
        strings_list = json.load(file)
    return strings_list


def _create_absolute_file_path(path_relative):
    """Given a path relative to the main.py, construct the absolute path."""
    directory_path = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.normpath(os.path.join(directory_path, path_relative))
    return absolute_path


if __name__ == "__main__":

    main()
