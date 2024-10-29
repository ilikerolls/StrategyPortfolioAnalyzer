import pandas as pd
from dataclasses import dataclass

from src.conf_setup import logger
from src.data.types.schema_data_trades import SchemaDT

@dataclass
class PortfolioStats:
    pass

@dataclass
class StrategyStats:
    """Class to hold Strategy Statistics. It only gets updated """
    name: str = ''
    rows: int = 0
    daily_df: pd.DataFrame = pd.DataFrame

class AnalyzeDataTrades:
    """Analyze and Combine Strategy Data such as Max Drawdown for Portfolio"""

    trade_data: dict[str, pd.DataFrame] = {}
    # Should only be accessed through get_strat_stats method
    _strat_stats: dict[str, StrategyStats] = {}

    def combine_strat_stats(self, strat_names: list) -> pd.DataFrame:
        # create a list of selected strategy data frames
        strat_stat_list = []
        for strat_name in strat_names:
            strat_stat_list.append(self.get_strat_stats(strat_name=strat_name).daily_df)
        # Combine to 1 Dataframe
        combined_df = pd.concat(objs=strat_stat_list)
        # Group By All Dataframes Combined to get our Total Daily PnL & Daily Cumulative Profits
        daily_pnl: pd.Series = combined_df.groupby(by=['Exit time'])['Profit'].sum()
        #TODO: cumsum() "may" not be calculating as expected or it could be a Data error?
        cum_sum: pd.Series = daily_pnl.cumsum()
        combined_profit_cum_df = pd.DataFrame(data={'Total Profit': daily_pnl, 'Cum. net profit': cum_sum}, index=SchemaDT.create_dt_idx(dates=daily_pnl.index))
        return combined_profit_cum_df

    def get_daily_max_dd(self, sel_strats_df: pd.DataFrame) -> float:
        """
        Get Drawdown for a portfolio of Strategies
        :param sel_strats_df: Combined Strategies Selected Dataframe
        :return: Combined Max DrawDown
        """
        highest_pnl = 0.0
        daily_cum_dd = {'Exit time': [], 'Cum_DD': []}
        # daily_date = date(index), cum_pnl = 'Cum. net profit'(column)
        for daily_date, cum_pnl in sel_strats_df['Cum. net profit'].items():
            if cum_pnl > highest_pnl: highest_pnl = cum_pnl
            daily_cum_dd['Exit time'].append(daily_date)
            # Calculate Cumulative DrawDown
            Daily_DD = highest_pnl if cum_pnl != 0 else 0.0
            Cum_DD = min((cum_pnl - Daily_DD), 0.0)
            daily_cum_dd['Cum_DD'].append(Cum_DD)
        daily_dd = round(min(daily_cum_dd['Cum_DD']), 2)

        return daily_dd

    def get_portfolio_calc_stats(self, strat_names: list) -> float:
        """
        Get Statistics for the Portfolio Calculator page based on the Strategies Selected
        :param strat_names: A list of Strategy Names to get Statistics for
        :return: A list of statistics
        """
        combined_stats_df = self.combine_strat_stats(strat_names=strat_names)
        total_max_dd = self.get_daily_max_dd(sel_strats_df=combined_stats_df)
        return total_max_dd

    def get_strat_stats(self, strat_name: str) -> StrategyStats:
        """
        Strategy Dataclasses should ONLY be retrieved through this method
        :param strat_name: Strategy Name
        :return: An up to date StrategyStats DataClass for the Strategy Name
        """
        if strat_name not in self._strat_stats.keys():
            self._strat_stats[strat_name] = StrategyStats(name=strat_name)
        self._strat_stats[strat_name] = self._update_strat_dataclass(strat_stats_obj=self._strat_stats[strat_name])
        return self._strat_stats[strat_name]

    def _update_strat_dataclass(self, strat_stats_obj: StrategyStats):
        """
        Create Strategy Data Class with Daily PnL and Daily Cumulative PnL
        :param strat_stats_obj: The strategy's StrategyStats Object
        """
        strat_df = self.trade_data[strat_stats_obj.name]
        strat_df_len = len(strat_df)
        # Only update Strategy's Stats Dataclass if number of records has changed. Otherwise, return cached Dataclass
        if strat_df_len != strat_stats_obj.rows:
            daily_pnl = strat_df.groupby(strat_df['Exit time'].dt.date)['Profit'].sum()
            daily_cum_pnl = strat_df.groupby(strat_df['Exit time'].dt.date)['Cum. net profit'].last()
            # strat_stats_obj.daily_df = pd.concat([daily_pnl, daily_cum_pnl], axis=1)
            strat_stats_obj.daily_df =  pd.DataFrame(data={'Profit': daily_pnl, 'Cum. net profit': daily_cum_pnl}, index=SchemaDT.create_dt_idx(dates=daily_pnl.index))
            logger.debug(
                f"{strat_stats_obj.name} - Updated Daily Stats DataClass Cache as there were new records. Previous row Count: {strat_df_len} Current Row Count: {strat_stats_obj.rows}.")
            strat_stats_obj.rows = strat_df_len
        return strat_stats_obj