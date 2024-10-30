import pandas as pd

from src.conf_setup import logger
from src.data.analyzers.StrategyStats import StrategyStats
from src.data.analyzers.portfolio_calc import PortfolioCalculator
from src.data.types.schema_data_trades import SchemaDT

class AnalyzeDataTrades:
    """Analyze and Combine Strategy Data such as Max Drawdown for Portfolio"""

    trade_data: dict[str, pd.DataFrame] = {}
    # Should only be accessed through get_strat_stats method
    _strat_stats: dict[str, StrategyStats] = {}

    def get_portfolio_calc_stats(self, strat_names: list) -> PortfolioCalculator:
        """
        Get Statistics for the Portfolio Calculator page based on the Strategies Selected
        :param strat_names: A list of Strategy Names to get Statistics for
        :return: PortfolioCalculator Dataclass with Calculations of Profit, Drawdown, etc..
        """
        # Get Strategy StrategyStats Objects
        sel_strats_ss = [self.get_strat_stats(strat_name=strat_name) for strat_name in strat_names]
        return PortfolioCalculator(sel_strats_ss=sel_strats_ss)

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