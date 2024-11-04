import time
from dataclasses import dataclass
import pandas as pd

from src.conf_setup import logger
from src.data.types.schema_data_trades import SchemaDT
from src.data.analyzers.StrategyStats import StrategyStats


@dataclass
class PortfolioCalculator:
    """
    Class for Portfolio Calculater Page
    Usage: PortfolioCalculator(sel_strats_ss=[StrategyStats_obj1, StrategyStats_obj2, StrategyStats_obj3])
    """
    # Selected Strategies Dataframe
    sel_strats_ss: list[StrategyStats]
    net_profit: float = 0.0
    max_drawdown: float = 0.0
    return_to_dd: float = 0.0
    # req_daytrade_capital_cur: float = 0.0
    # daily_win_rate: float = 0.0
    # largest_losing_day: datetime = None
    # largest_losing_day_cap: float = 0.0
    # largest_winning_day: datetime = None
    # largest_winning_day_cap: float = 0.0

    def __post_init__(self):
        # Only do Calculations if we have more than 1 strategy selected. Otherwise, return 0's for empty Strategy List
        if len(self.sel_strats_ss) > 0:
            start_time = time.time()
            self._combined_strats_df = self._combine_strat_stats()
            # Store Strategy Names
            self.strat_names: list = [strat_ss.name for strat_ss in self.sel_strats_ss]
            self._set_net_profit()
            self._set_daily_max_dd()
            self._set_return_to_dd_ratio()
            elapsed_time = round((time.time() - start_time), 4)
            if elapsed_time > 10:
                logger.warning(f"It took {elapsed_time} Seconds to build this Portfolio of {len(self.strat_names)} Strategies. Strategy Names: {self.strat_names}")

    def _combine_strat_stats(self) -> pd.DataFrame:
        # create a list of selected strategy data frames
        strat_stat_list = [strat_ss.daily_df for strat_ss in self.sel_strats_ss]
        # Combine to 1 Dataframe
        combined_df = pd.concat(objs=strat_stat_list)
        # Group By All Dataframes Combined to get our Total Daily PnL & Daily Cumulative Profits
        daily_pnl: pd.Series = combined_df.groupby(by=[SchemaDT.DT_INDEX_NAME])['Profit'].aggregate('sum')
        #TODO: cumsum() "may" not be calculating as expected or it could be a Data error?
        cum_sum: pd.Series = daily_pnl.cumsum()
        #NOTE: Do we really need to sort the Datetimes? It takes 0.001 second more per strategy
        return pd.DataFrame(data={'Profit': daily_pnl, 'Cum. net profit': cum_sum},
                     index=SchemaDT.create_dt_idx(dates=daily_pnl.index)).sort_index(ascending=True)

    def _set_daily_max_dd(self):
        """ Sets Drawdown for a portfolio of Strategies """
        cum_net_profit = self.combined_strats_df['Cum. net profit']
        running_max = cum_net_profit.cummax()
        drawdown = cum_net_profit - running_max
        self.max_drawdown = round(drawdown.min(), 2)

    def _set_net_profit(self):
        """Get Total Net Profit for Selected Strategies"""
        self.net_profit = round(self.combined_strats_df['Cum. net profit'].iloc[-1], 2)

    def _set_return_to_dd_ratio(self):
        """Calculate Return to Drawdown Ratio"""
        if self.max_drawdown != 0:
            self.return_to_dd = round(abs(self.net_profit / self.max_drawdown), 2)

    @property
    def combined_strats_df(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        :param start_date: [Optional] A string in format 2022-01-01 Representing the Start Date to select from the
        Combined Strategies Dataframe. Default is ALL(earliest) Dates
        :param end_date: [Optional] A string in format 2024-12-31 Representing the End Date to select from the
        Combined Strategies Dataframe. Default is ALL(latest) Dates
        :return: A combined strategy Pandas Dataframe from self._combined_strats_df
        """
        if start_date is not None:
            return self._combined_strats_df.loc[start_date:end_date]
        return self._combined_strats_df