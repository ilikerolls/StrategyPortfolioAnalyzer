from dataclasses import dataclass, fields
import pandas as pd

from src.data.types.schema_data_trades import SchemaDT


@dataclass
class StrategyStats:
    """Class to hold Strategy Statistics. It only gets updated """
    # Name of Strategy
    name: str
    # Rows in Strategy
    rows: int = 0
    df_start_date: str = None
    df_end_date: str = None
    net_profit: float = 0.0
    max_drawdown: float = 0.0
    return_to_dd: float = 0.0

    def __post_init__(self):
        # Index will be a Datetime Index called 'Exit time'. Dataframe will have ['Profit', 'Cum. net profit'] columns
        self.daily_df: pd.DataFrame = pd.DataFrame()

    def copy_shallow(self):
        """
        :return: A Copy of this StrategyStats object only containing the fields and not internals like the daily_df
        """
        return StrategyStats(
            **{field.name: getattr(self, field.name) for field in fields(self)}
        )

    def create_daily_df(self, strat_df: pd.DataFrame):
        """
        Create a Daily Dataframe for the Strategy and pick out the parts we need.
        :param strat_df: An Entire Strategy's Dataframe
        """
        daily_pnl = strat_df.groupby(strat_df['Exit time'].dt.date)['Profit'].sum()
        daily_cum_pnl = strat_df.groupby(strat_df['Exit time'].dt.date)['Cum. net profit'].last()
        self.daily_df = pd.DataFrame(data={'Profit': daily_pnl, 'Cum. net profit': daily_cum_pnl},
                     index=SchemaDT.create_dt_idx(dates=daily_pnl.index))
        self.rows = len(self.daily_df)
        self._update_df_stats()
        self.update_stats()

    def get_daily_max_dd(self, start_date: str = None, end_date: str = None) -> float:
        """Returns the Max Drawdown for a Strategy
        :param start_date: [Optional] Starting date to select from dataframe. Default: ALL Dates. Ex: 2024-01-01
        :param end_date: Date to Stop searching for Max Drawdown. Ex: 2024-12-31
        :return: A float of the Max Drawdown for Strategy
        """
        if start_date is None and end_date is None:
            return self.max_drawdown
        start_date = start_date if start_date is not None else self.df_start_date
        end_date = end_date if end_date is not None else self.df_end_date
        cum_net_profit = self.daily_df.loc[start_date:end_date, 'Cum. net profit']
        return self._calculate_drawdown(cum_net_profit)


    @staticmethod
    def _calculate_drawdown(cum_net_profit):
        """Helper method to calculate drawdown."""
        running_max = cum_net_profit.cummax()
        drawdown = cum_net_profit - running_max
        return round(drawdown.min(), 2)

    def _update_daily_df(self, start_date: str = None, end_date: str = None):
        """
        Update Strategy Statistics/Fields based on new dates
        :param start_date: [Optional] Starting date to select from dataframe. Default: ALL Dates. Ex: 2024-01-01
        :param end_date: [Optional] End Date to select from dataframe. Default: ALL Dates Ex: 2024-12-32
        """
        start_date = pd.to_datetime(start_date) if start_date is not None else self.daily_df.index.min()
        end_date = pd.to_datetime(end_date) if end_date is not None else self.daily_df.index.max()
        daily_pnl = self.daily_df.loc[start_date:end_date, 'Profit']
        cum_sum: pd.Series = daily_pnl.cumsum()
        self.daily_df = pd.DataFrame(data={'Profit': daily_pnl, 'Cum. net profit': cum_sum},
                     index=SchemaDT.create_dt_idx(dates=daily_pnl.index)).sort_index(ascending=True)
        self._update_df_stats()

    def _update_df_stats(self):
        """Update self.df_start_date, self.df_end_date, self.rows of Dataframe for performance"""
        self.df_start_date = self.daily_df.index.min()
        self.df_end_date = self.daily_df.index.max()
        self.rows = len(self.daily_df)

    def _set_daily_max_dd(self):
        """ Sets Drawdown for a portfolio of Strategies """
        cum_net_profit = self.daily_df['Cum. net profit']
        self.max_drawdown = self._calculate_drawdown(cum_net_profit)

    def _set_net_profit(self):
        """Get Total Net Profit for Selected Strategies"""
        if self.rows > 0:
            self.net_profit = round(self.daily_df['Cum. net profit'].iloc[-1], 2)

    def _set_return_to_dd_ratio(self):
        """Calculate Return to Drawdown Ratio"""
        if self.max_drawdown != 0:
            self.return_to_dd = round(abs(self.net_profit / self.max_drawdown), 2)

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