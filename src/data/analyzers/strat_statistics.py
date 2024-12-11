import pandas as pd

class StratStatistics:
    """Base Class for Calculating Statistics on both a Single Strategy and Portfolio of Strategies"""

    # Capital Required by Max DrawDown Multiplier
    REQ_CAP_MAX_DD_MULT: float = 1.5

    def __init__(self, start_date: str = None, end_date: str = None):
        """
        :param start_date: Set Start Date for Strategy Results
        :param end_date: Set End Date for Strategy Results
        """
        self.strats_df: pd.DataFrame | None = None
        self.trade_count: int = 0
        self.start_date: str | None = start_date
        self.end_date: str | None = end_date
        self.net_profit: float = 0.0
        self.max_drawdown: float = 0.0
        self.return_to_dd: float = 0.0
        self.req_cap_daytrade: float = 0.0
        self.daily_win_rate: float = 0.0
        # largest_losing_day: datetime = None
        # largest_losing_day_cap: float = 0.0
        # largest_winning_day: datetime = None
        # largest_winning_day_cap: float = 0.0

    @staticmethod
    def _calculate_drawdown(cum_net_profit: pd.Series):
        """Helper method to calculate drawdown."""
        running_max = cum_net_profit.cummax()
        drawdown = cum_net_profit - running_max
        return round(drawdown.min(), 2)

    def _set_daily_max_dd(self):
        """ Sets Drawdown for a Strategy or portfolio of Strategies """
        cum_net_profit = self.strats_df['Cum. net profit']
        self.max_drawdown = self._calculate_drawdown(cum_net_profit)

    def _set_net_profit(self):
        """Get Total Net Profit for Selected Strategies"""
        if self.trade_count > 0:
            self.net_profit = round(self.strats_df['Cum. net profit'].iloc[-1], 2)

    def _set_req_cap_daytrade(self):
        """Calculate Required Day Trade Capital for Portfolio of Strategies. Formula:
        abs(Max Drawdown * REQ_CAP_MAX_DD_MULT) - MIN(Cumulative PnL)"""
        self.req_cap_daytrade = abs(self.max_drawdown * self.REQ_CAP_MAX_DD_MULT) - self.strats_df['Cum. net profit'].min()

    def _set_return_to_dd_ratio(self):
        """Calculate Return to Drawdown Ratio"""
        if self.max_drawdown != 0:
            self.return_to_dd = round(abs(self.net_profit / self.max_drawdown), 2)

    def _set_win_rate(self):
        """Calculate Daily Win Rate for Portfolio of Strategies"""
        if self.trade_count > 0:
            daily_pnl:pd.Series = self.strats_df['Profit']
            self.daily_win_rate = (daily_pnl > 0).sum() / len(daily_pnl) * 100