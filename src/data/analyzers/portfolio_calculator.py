import time
from copy import deepcopy
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
    start_date: str = None
    end_date: str = None
    net_profit: float = 0.0
    max_drawdown: float = 0.0
    return_to_dd: float = 0.0
    strat_names: list = list
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
            self._update_strat_df_dates()
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
        tmp_combined_df = pd.concat(objs=strat_stat_list)
        # Group By All Dataframes Combined to get our Total Daily PnL & Daily Cumulative Profits
        daily_pnl: pd.Series = tmp_combined_df.groupby(by=[SchemaDT.DT_INDEX_NAME])['Profit'].sum()
        cum_sum: pd.Series = daily_pnl.cumsum()
        return pd.DataFrame(data={'Profit': daily_pnl, 'Cum. net profit': cum_sum},
                     index=SchemaDT.create_dt_idx(dates=daily_pnl.index)).sort_index(ascending=True)

    def _update_strat_df_dates(self):
        """Update Individual StrategyStats Objects to Selected Dates & Create a Copy of them if there's a start_date"""
        # Loop through and only get Start & End Dates from Dataframe
        if self.start_date is not None:
            tmp_sel_strats_ss = []
            # Set Individual Strategies to a Selected Date Permanently within this Object
            for strat_ss in self.sel_strats_ss:
                copied_strat_ss = deepcopy(strat_ss)
                copied_strat_ss.daily_df = strat_ss.daily_df.loc[self.start_date: self.end_date]
                daily_pnl: pd.Series = copied_strat_ss.daily_df.groupby(by=[SchemaDT.DT_INDEX_NAME])['Profit'].sum()
                cum_sum: pd.Series = daily_pnl.cumsum()
                copied_strat_ss.daily_df = pd.DataFrame(data={'Profit': daily_pnl, 'Cum. net profit': cum_sum},
                             index=SchemaDT.create_dt_idx(dates=daily_pnl.index)).sort_index(ascending=True)
                tmp_sel_strats_ss.append(copied_strat_ss)
            self.sel_strats_ss = tmp_sel_strats_ss

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
    def combined_strats_df(self) -> pd.DataFrame:
        """:return: A combined strategy Pandas Dataframe from self._combined_strats_df"""
        return self._combined_strats_df