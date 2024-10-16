__author__ = "Marcis Greenwood"
__email__ = "greenwood.marcis@hotmail.com"
__license__ = "GPL"
from src.conf_setup import logger, APP_NAME
from src.data_loader import DataloaderCSV

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logger.info(f'Starting {APP_NAME}')
    data_loader = DataloaderCSV()
    data_loader.load_data()