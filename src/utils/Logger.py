import logging
import colorlog

logger_level_dict = {'none': logging.CRITICAL + 1,
                     'critical': logging.CRITICAL,
                     'info': logging.INFO,
                     'debug': logging.DEBUG,
                     'trace': logging.DEBUG - 1}

colorlog_colors_dict = {
    'DEBUG': 'reset',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red,bg_white',
}

colorlog_format = '%(log_color)s %(name)s: [%(levelname)s] - %(message)s'


class Logger(logging.Logger):
    """Wrapper to the logging.Logger with an easier constructor."""

    def __init__(self, name: str, logging_level_str: str = 'none'):

        logging_level_str = logging_level_str.lower()  # make it lowercase

        # Set the logging level
        if logging_level_str in logger_level_dict.keys():
            level = logger_level_dict[logging_level_str]
        else:
            raise (KeyError('Check logging_level_str'))

        # Create Logging object
        super().__init__(name, level)

        # Create Console (std output) handler

        # Formatter of console handler
        self.console_formatter = colorlog.ColoredFormatter(
            colorlog_format,
            log_colors=colorlog_colors_dict,
            secondary_log_colors={}
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.console_formatter)
        # Add console handler to logger
        self.addHandler(console_handler)

    def logToFile(self, filename: str, formatter=None):
        """Also dumps the logs to the file."""
        if formatter is None:
            formatter = self.console_formatter

        file_handler = logging.FileHandler(filename, encoding='utf-8')
        file_handler.setFormatter(formatter)

        self.info(f'Logging file is specified as: {filename}')
        self.addHandler(file_handler)


if __name__ == "__main__":
    logger = Logger('LoggerFunctionality', 'debug')
    logger.info("Deneme -> Info")
    logger.debug("Deneme -> Debug")
