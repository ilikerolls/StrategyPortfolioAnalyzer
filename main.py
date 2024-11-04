__author__ = "Marcis Greenwood"
__email__ = "greenwood.marcis@hotmail.com"
__license__ = "GPL"

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
    test_strats = ['MomentumNQ', 'CourseVWAPStrategy']
    # test_strats = ['MomentumNQ']
    # portfolio_stats = data_loader.data_trades.get_portfolio_calc_stats(strat_names=test_strats)
    # logger.info(f"Total Combined Statistics for Strategies MomentumNQ and CourseVWAPStrategy are\nNet Profit: {portfolio_stats.net_profit}\nMax Drawdown: {portfolio_stats.max_drawdown}\nReturn to Drawdown: {portfolio_stats.return_to_dd}")
    start_dashboard()
    logger.info(f'{APP_NAME}: Ended')