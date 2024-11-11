__author__ = "Marcis Greenwood"
__email__ = "greenwood.marcis@hotmail.com"
__license__ = "proprietary"
"This software is proprietary and protected by copyright laws. You are granted a non-transferable license to use this software solely for your own internal purposes. Any attempt to modify, distribute, or reverse engineer this software without prior written consent from Marcis Greenwood is strictly prohibited."

from src.UI.app import start_dashboard
from src.conf_setup import logger, APP_NAME
from src.data.loaders.data_loader import DataLoaderCSV

if __name__ == '__main__':
    logger.info(f'{APP_NAME}: Started')
    data_loader = DataLoaderCSV()
    data_loader.load_strat_csvs()
    # Monitor for CSVS every this amount of seconds in a separate thread
    data_loader.monitor_csvs(seconds=120)
    # The following 2 lines are for testing and can be removed in the future
    start_dashboard()
    logger.info(f'{APP_NAME}: Ended')