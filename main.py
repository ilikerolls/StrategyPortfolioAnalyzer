__author__ = "Marcis Greenwood"
__email__ = "greenwood.marcis@hotmail.com"
__license__ = "GPL"

from src.conf_setup import logger, APP_NAME
from src.data.loaders.data_loader import DataLoaderCSV

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logger.info(f'{APP_NAME}: Started')
    data_loader = DataLoaderCSV()
    data_trades = data_loader.load_strat_csvs()
    daily_returns = data_trades.get_daily_returns(strat_name='MomentumNQ')
    logger.info(f"Daily Returns for MomentumNQ are:\n{daily_returns}")
    logger.info(f'{APP_NAME}: Ended')