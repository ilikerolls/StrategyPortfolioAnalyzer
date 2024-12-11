import time
from copy import deepcopy
import pandas as pd

from src.conf_setup import logger
from src.data.analyzers.strat_statistics import StratStatistics
from src.data.types.schema_data_trades import SchemaDT
from src.data.analyzers.StrategyStats import StrategyStats

class PortfolioCalculator(StratStatistics):
    """Class for Portfolio Calculater Page"""

    def __init__(self, sel_strats_ss: list[StrategyStats], start_date: str = None, end_date: str = None):
        """
        Usage: PortfolioCalculator(sel_strats_ss=[StrategyStats_obj1, StrategyStats_obj2, StrategyStats_obj3])
        :param sel_strats_ss: A list of StrategyStats objects to calculate in our Portfolio
        :param start_date: Set Start Date for Strategy Results
        :param end_date: Set End Date for Strategy Results
        """
        self.sel_strats_ss = sel_strats_ss
        self.strat_names: list = []
        StratStatistics.__init__(self, start_date=start_date, end_date=end_date)
        # Only do Calculations if we have more than 1 strategy selected. Otherwise, return 0's for empty Strategy List
        if len(self.sel_strats_ss) > 0:
            start_time = time.time()
            self._update_strat_df_dates()
            self._combine_strat_stats()
            # Store Strategy Names
            self.strat_names = [strat_ss.name for strat_ss in self.sel_strats_ss]
            self._set_net_profit()
            self._set_daily_max_dd()
            self._set_return_to_dd_ratio()
            self._set_req_cap_daytrade()
            self._set_win_rate()
            elapsed_time = round((time.time() - start_time), 4)
            if elapsed_time > 10:
                logger.warning(f"It took {elapsed_time} Seconds to build this Portfolio of {len(self.strat_names)} Strategies. Strategy Names: {self.strat_names}")

    def _combine_strat_stats(self):
        # create a list of selected strategy data frames
        strat_stat_list = [strat_ss.strats_df for strat_ss in self.sel_strats_ss]
        # Combine to 1 Dataframe
        tmp_combined_df = pd.concat(objs=strat_stat_list)
        # Group By All Dataframes Combined to get our Total Daily PnL & Daily Cumulative Profits
        daily_pnl: pd.Series = tmp_combined_df.groupby(by=[SchemaDT.DT_INDEX_NAME])['Profit'].sum()
        cum_sum: pd.Series = daily_pnl.cumsum()
        self.strats_df = pd.DataFrame(data={'Profit': daily_pnl, 'Cum. net profit': cum_sum},
                     index=SchemaDT.create_dt_idx(dates=daily_pnl.index)).sort_index(ascending=True)
        self.trade_count = len(self.strats_df)


    def _update_strat_df_dates(self):
        """Update Individual StrategyStats Objects to Selected Dates & Create a Copy of them if there's a start_date"""
        # Loop through and only get Start & End Dates from Dataframe
        if self.start_date is None and self.end_date is None:
            return
        tmp_sel_strats_ss = []
        # Set Individual Strategies to a Selected Date Permanently within this Object
        for strat_ss in self.sel_strats_ss:
            copied_strat_ss = deepcopy(strat_ss)
            start_date = self.start_date if self.start_date is not None else copied_strat_ss.strats_df.index.min()
            end_date = self.end_date if self.end_date is not None else copied_strat_ss.strats_df.index.max()
            copied_strat_ss.strats_df = strat_ss.strats_df.loc[start_date: end_date]
            daily_pnl: pd.Series = copied_strat_ss.strats_df.groupby(by=[SchemaDT.DT_INDEX_NAME])['Profit'].sum()
            cum_sum: pd.Series = daily_pnl.cumsum()
            copied_strat_ss.strats_df = pd.DataFrame(data={'Profit': daily_pnl, 'Cum. net profit': cum_sum},
                                                      index=SchemaDT.create_dt_idx(dates=daily_pnl.index)).sort_index(ascending=True)
            tmp_sel_strats_ss.append(copied_strat_ss)
        self.sel_strats_ss = tmp_sel_strats_ss

    @property
    def combined_strats_df(self) -> pd.DataFrame:
        """:return: A combined strategy Pandas Dataframe from self.strats_df"""
        return self.strats_df