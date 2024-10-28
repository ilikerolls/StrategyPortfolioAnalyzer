__author__ = "Marcis Greenwood"
__email__ = "greenwood.marcis@hotmail.com"
__license__ = "GPL"

from src.UI.app import start_dashboard
from src.conf_setup import logger, APP_NAME
from src.data.loaders.data_loader import DataLoaderCSV

if __name__ == '__main__':
    logger.info(f'{APP_NAME}: Started')
    data_loader = DataLoaderCSV()
    # Monitor for CSVS every this amount of seconds in a separate thread
    data_loader.monitor_csvs(seconds=60)
    # The following 2 lines are for testing and can be removed in the future
    total_max_dd = data_loader.data_trades.get_portfolio_calc_stats(strat_names=['MomentumNQ', 'CourseVWAPStrategy'])
    logger.info(f"Total Combined Max Drawdown for Strategies MomentumNQ and CourseVWAPStrategy are: {total_max_dd}")
    start_dashboard()
    logger.info(f'{APP_NAME}: Ended')