from itertools import combinations
import pandas as pd

from src.conf_setup import logger
from src.data.analyzers.StrategyStats import StrategyStats
from src.data.analyzers.portfolio_calculator import PortfolioCalculator
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

    def optimize_portfolio(self, strat_names: list = None, top_ct: int = 3) -> list[PortfolioCalculator]:
        """
        Optimize a list of Strategy Names and return the top [top_ct] best
        :param strat_names: [Optional] A list of Strategy names to be Optimized. Default uses ALL Strategies
        :param top_ct: [Optional] Number of top best strategies to return
        :return: A list of top PortfolioCalculator Object performers
        """
        if strat_names is None:
            strat_names = self.strats_to_list()
        # Top PortfolioCalculator Strategy Objects to return
        top_strats = []
        for L in range(len(strat_names) + 1):
            for strat_comb in combinations(strat_names, L):
                if len(strat_comb) == 0: continue
                portfolio_calc = self.get_portfolio_calc_stats(strat_names=list(strat_comb))
                top_strats.append(portfolio_calc)
                # Sort PortfolioCalculator objects based on the value returned by get_value and select top top_ct(3)
                top_strats = sorted(top_strats, key=lambda p_calc: p_calc.return_to_dd, reverse=True)[:top_ct]
        return top_strats

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
            strat_stats_obj.rows = strat_df_len
        return strat_stats_obj

    def strats_to_list(self) -> list:
        """
        :return: A list of Loaded Strategies
        """
        return list(self.trade_data.keys())