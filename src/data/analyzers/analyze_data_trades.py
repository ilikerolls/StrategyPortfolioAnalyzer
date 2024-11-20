from copy import deepcopy
from itertools import combinations
import pandas as pd

from src.data.analyzers.StrategyStats import StrategyStats
from src.data.analyzers.portfolio_calculator import PortfolioCalculator

class AnalyzeDataTrades:
    """Analyze and Combine Strategy Data such as Max Drawdown for Portfolio"""

    trade_data: dict[str, pd.DataFrame] = {}
    # Should only be accessed through get_strat_stats method
    _strat_stats: dict[str, StrategyStats] = {}

    def get_calc_portfolio_stats(self, strat_names: list, start_date: str = None, end_date: str = None) -> PortfolioCalculator:
        """
        Get Statistics for the Portfolio Calculator page based on the Strategies Selected
        :param strat_names: A list of Strategy Names to get Statistics for
        :param start_date: [Optional] Starting date to select from dataframe. Default: ALL Dates
        :param end_date: [Optional] End Date to select from dataframe. Default: ALL Dates
        :return: PortfolioCalculator Dataclass with Calculations of Profit, Drawdown, etc
        """
        # Get Strategy StrategyStats Objects
        sel_strats_ss = [self.get_strat_stats(strat_name=strat_name) for strat_name in strat_names]
        return PortfolioCalculator(sel_strats_ss=sel_strats_ss, start_date=start_date, end_date=end_date)

    def get_live_portfolio_stats(self, strat_name_dt: dict) -> PortfolioCalculator:
        """
        Get Live Portfolio Statistics
        :param strat_name_dt: A Dict with Strategy Names & Live Start Dates Ex: {'strat1': 'start_date', 'strat2': '2024-01-01'}
        :return: PortfolioCalculator Dataclass with Calculations of Profit, Drawdown, etc
        """
        sel_strats_ss = []
        for strat_name, live_date in strat_name_dt.items():
            strat_ss = self.get_strat_stats(strat_name=strat_name)
            strat_ss_copied = deepcopy(strat_ss)
            strat_ss_copied.update_stats(start_date=live_date)
            sel_strats_ss.append(strat_ss_copied)
        return PortfolioCalculator(sel_strats_ss=sel_strats_ss)

    def get_strat_stats(self, strat_name: str) -> StrategyStats:
        """
        Strategy Dataclasses should ONLY be retrieved through this method
        :param strat_name: Strategy Name
        False = Return Original StrategyStats. But if daily_df dataframe is modified it would be modified globally!
        :return: An up to date StrategyStats DataClass for the Strategy Name
        """
        if strat_name not in self._strat_stats.keys():
            self._strat_stats[strat_name] = StrategyStats(name=strat_name)
        self._strat_stats[strat_name] = self._update_strat_dataclass(strat_stats_obj=self._strat_stats[strat_name])
        return self._strat_stats[strat_name]

    def optimize_portfolio(self, strat_names: list = None, start_date: str = None, end_date: str = None, top_ct: int = 5) -> list[PortfolioCalculator]:
        """
        Optimize a list of Strategy Names and return the top [top_ct] best
        :param strat_names: [Optional] A list of Strategy names to be Optimized. Default uses ALL Strategies
        :param start_date: [Optional] Starting date to select from dataframe. Default: ALL Dates
        :param end_date: [Optional] End Date to select from dataframe. Default: ALL Dates
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
                portfolio_calc = self.get_calc_portfolio_stats(strat_names=list(strat_comb), start_date=start_date, end_date=end_date)
                top_strats.append(portfolio_calc)
                # Sort PortfolioCalculator objects based on the value returned by get_value and select top top_ct(3)
                top_strats = sorted(top_strats, key=lambda p_calc: p_calc.return_to_dd, reverse=True)[:top_ct]
        return top_strats

    def _update_strat_dataclass(self, strat_stats_obj: StrategyStats) -> StrategyStats:
        """
        Create Strategy Data Class with Daily PnL and Daily Cumulative PnL
        :param strat_stats_obj: The strategy's StrategyStats Object
        """
        strat_df = self.trade_data[strat_stats_obj.name]
        # Only update Strategy's Stats Dataclass if number of records has changed. Otherwise, return cached Dataclass
        if len(strat_df) != strat_stats_obj.rows:
            strat_stats_obj.create_daily_df(strat_df=strat_df)
        return strat_stats_obj

    def strats_to_list(self) -> list:
        """
        :return: A list of Loaded Strategies
        """
        return list(self.trade_data.keys())