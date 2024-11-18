from dataclasses import dataclass
import pandas as pd

@dataclass
class StrategyStats:
    """Class to hold Strategy Statistics. It only gets updated """
    # Name of Strategy
    name: str = ''
    # Rows in Strategy
    rows: int = 0
    # Index will be a Datetime Index called 'Exit time'. Dataframe will have 'Profit' and 'Cum. net profit' columns
    daily_df: pd.DataFrame = pd.DataFrame

    def get_daily_max_dd(self, end_date = None) -> float:
        """Returns the Max Drawdown for a Strategy
        :param end_date: Date to Stop searching for Max Drawdown
        :return: A float of the Max Drawdown for Strategy
        """
        cum_net_profit = self.daily_df['Cum. net profit'].loc[:end_date]
        running_max = cum_net_profit.cummax()
        drawdown = cum_net_profit - running_max
        return round(drawdown.min(), 2)