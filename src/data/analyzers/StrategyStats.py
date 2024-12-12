import pandas as pd

from src.data.analyzers.strat_statistics import StratStatistics

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
        super().__init__(start_date=start_date, end_date=end_date)
        self.name = name

    def create_daily_df(self, strat_df: pd.DataFrame):
        """
        Create a Daily Dataframe for the Strategy and pick out the parts we need.
        :param strat_df: An Entire Strategy's Dataframe
        """
        daily_pnl = strat_df.groupby(strat_df['Exit time'].dt.date)['Profit'].sum()
        self.create_daily_strats_df(daily_pnl=daily_pnl)
        self.update_stats()

    def get_daily_max_dd(self, start_date: str = None, end_date: str = None) -> float:
        """Returns the Max Drawdown for a Strategy
        :param start_date: [Optional] Starting date to select from dataframe. Default: ALL Dates. Ex: 2024-01-01
        :param end_date: Date to Stop searching for Max Drawdown. Ex: 2024-12-31
        :return: A float of the Max Drawdown for Strategy
        """
        if start_date is None and end_date is None:
            return self.max_drawdown
        start_date = start_date or self.df_start_date
        end_date = end_date or self.df_end_date
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
        self.create_daily_strats_df(daily_pnl=daily_pnl)

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