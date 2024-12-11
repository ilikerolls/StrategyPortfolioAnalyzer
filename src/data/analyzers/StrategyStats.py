import pandas as pd

from src.data.analyzers.strat_statistics import StratStatistics
from src.data.types.schema_data_trades import SchemaDT

class StrategyStats(StratStatistics):
    """
    Class to hold 1 Strategies Statistics. It only gets updated when they're New Trades
    self.strats_df = Pandas Dataframe where Index will be a Datetime Index called 'Exit time'. Dataframe will have ['Profit', 'Cum. net profit'] columns
    """

    def __init__(self, name: str, start_date: str = None, end_date: str = None):
        """
        :param name: Name of Strategy
        :param start_date: Set Start Date for Strategy Results
        :param end_date: Set End Date for Strategy Results
        """
        StratStatistics.__init__(self, start_date=start_date, end_date=end_date)
        self.name = name

    def create_daily_df(self, strat_df: pd.DataFrame):
        """
        Create a Daily Dataframe for the Strategy and pick out the parts we need.
        :param strat_df: An Entire Strategy's Dataframe
        """
        daily_pnl = strat_df.groupby(strat_df['Exit time'].dt.date)['Profit'].sum()
        daily_cum_pnl = strat_df.groupby(strat_df['Exit time'].dt.date)['Cum. net profit'].last()
        self._update_daily_df_internal(daily_pnl, daily_cum_pnl)
        self.update_stats()

    def get_daily_max_dd(self, start_date: str = None, end_date: str = None) -> float:
        """Returns the Max Drawdown for a Strategy
        :param start_date: [Optional] Starting date to select from dataframe. Default: ALL Dates. Ex: 2024-01-01
        :param end_date: Date to Stop searching for Max Drawdown. Ex: 2024-12-31
        :return: A float of the Max Drawdown for Strategy
        """
        if start_date is None and end_date is None:
            return self.max_drawdown
        start_date = start_date if start_date is not None else self.start_date
        end_date = end_date if end_date is not None else self.end_date
        cum_net_profit = self.strats_df.loc[start_date:end_date, 'Cum. net profit']
        return self._calculate_drawdown(cum_net_profit)

    def _update_daily_df(self, start_date: str = None, end_date: str = None):
        """
        Update Strategy Statistics/Fields based on new dates
        :param start_date: [Optional] Starting date to select from dataframe. Default: ALL Dates. Ex: 2024-01-01
        :param end_date: [Optional] End Date to select from dataframe. Default: ALL Dates Ex: 2024-12-32
        """
        start_date = pd.to_datetime(start_date) if start_date is not None else self.strats_df.index.min()
        end_date = pd.to_datetime(end_date) if end_date is not None else self.strats_df.index.max()
        daily_pnl = self.strats_df.loc[start_date:end_date, 'Profit']
        cum_sum: pd.Series = daily_pnl.cumsum()
        self._update_daily_df_internal(daily_pnl, cum_sum)

    def _update_daily_df_internal(self, daily_pnl: pd.Series, cum_net_profit: pd.Series):
        """Update self.strats_df, self.start_date, self.end_date, self.trade_count of Dataframe for performance
        :param daily_pnl: Panda Series containing Profit sum for each day
        :param cum_net_profit: Panda Series containing Cumulative Profit
        """
        self.strats_df = pd.DataFrame(data={'Profit': daily_pnl, 'Cum. net profit': cum_net_profit},
                                       index=SchemaDT.create_dt_idx(dates=daily_pnl.index)).sort_index(ascending=True)
        self.start_date = self.strats_df.index.min()
        self.end_date = self.strats_df.index.max()
        self.trade_count = len(self.strats_df)

    def update_stats(self, start_date: str = None, end_date: str = None):
        """
        Update Strategy Statistics/Fields based on new dates
        :param start_date: [Optional] Starting date to select from dataframe. Default: ALL Dates. Ex: 2024-01-01
        :param end_date: [Optional] End Date to select from dataframe. Default: ALL Dates Ex: 2024-12-32
        """
        if start_date is not None or end_date is not None:
            self._update_daily_df(start_date=start_date, end_date=end_date)
        self._set_net_profit()
        self._set_daily_max_dd()
        self._set_return_to_dd_ratio()
        self._set_win_rate()