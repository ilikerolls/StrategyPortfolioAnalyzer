import pandas as pd

from src.conf_setup import logger
from src.utils import accounting_to_num, to_datetime


class DataTrades:
    """Holds each Strategies Trade Data"""

    # Strategy Dataframe Columns/Headers
    strat_cols = ['Trade number','Instrument','Account','Strategy','Market pos.','Qty','Entry price','Exit price','Entry time','Exit time','Entry name', 'Exit name', 'Profit','Cum. net profit',
                  'Commission','MAE','MFE','ETD','Bars']
    strat_indexes = ['Entry time','Exit time']
    strat_col_dtypes = {'Trade number': pd.Series(dtype='string'), 'Instrument': pd.Series(dtype='string'),
                        'Account': pd.Series(dtype='string'),
                        'Strategy': pd.Series(dtype='string'), 'Market pos.': pd.Series(dtype='string'),
                        'Qty': pd.Series(dtype='float'),
                        'Entry price': pd.Series(dtype='float'), 'Exit price': pd.Series(dtype='float'),
                        'Entry time': pd.Series(dtype='datetime64[ns]'),
                        'Exit time': pd.Series(dtype='datetime64[ns]'), 'Entry name': pd.Series(dtype='string'),
                        'Exit name': pd.Series(dtype='string'), 'Profit': pd.Series(dtype='float'),
                        'Cum. net profit': pd.Series(dtype='float'), 'Commission': pd.Series(dtype='float'),
                        'MAE': pd.Float64Dtype, 'MFE': pd.Series(dtype='float'), 'ETD': pd.Series(dtype='float'),
                        'Bars': pd.Series(dtype='int')}
    # Data Converters
    data_converters = {'Profit': accounting_to_num,'Cum. net profit': accounting_to_num,
                         "Commission": accounting_to_num,'ETD': accounting_to_num, 'MAE': accounting_to_num,'MFE': accounting_to_num, 'Entry time': to_datetime, 'Exit time': to_datetime}

    def __init__(self):
        # Dictionary of Trade Data with trade_data['Strategy_Name'] = Pandas Dataframe of Trades
        self.trade_data: dict[str, pd.DataFrame] = {}

    def add_db_strat_trades(self, trades_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add a Strategy's trades Pandas Dataframe to the DataTrades Object
        :param trades_df: Pandas Dataframe with the Strategy's Trades
        :return: A Pandas Data from of the Added Strategy
        """
        strat_name = trades_df['Strategy'].iloc[0]
        self.trade_data[strat_name] = trades_df
        self.trade_data[strat_name].set_index(keys=DataTrades.strat_indexes, inplace=True, drop=False, verify_integrity=True)
        # read_parquet doesn't return all the correct Data Types, but at least the important ones "Entry time" "Exit time"
        # TODO: 1 option if we decide we need it is to re-apply DataTrades.strat_col_dtypes to ALL columns, but so far we don't need it
        # Data Types:\n{self.trade_data[strat_name].dtypes}
        logger.info(f"Loaded Strategy [{strat_name}] with [{len(self.trade_data[strat_name])}] Rows.")
        return self.trade_data[strat_name]

    def add_trade_data(self, row: dict):
        """
        Add a trade to a Strategy from a CSV file. NOTE: We need to do 1 line at a time, because a .csv file may contain
        multiple Strategy names in it.
        :param row: A Dictionary Row with same keys as self.strat_cols(Columns)
        """
        formatted_row: dict = self._format_row(row=row)
        strat_name = formatted_row['Strategy']
        # Creates a new Dataframe for the Strategy if one doesn't already Exist
        strat_df = self.get_strat_df(strat_name=strat_name)
        row_df = pd.DataFrame(data=[formatted_row.values()], columns=DataTrades.strat_cols)
        self.trade_data[strat_name] = pd.concat([strat_df, row_df])

    def _format_row(self, row: dict) -> dict:
        """
        Convert a Dict of Data to propper formatting our Dataframe Supports
        :param row: A dictionary of data including columns in strat_cols
        """
        new_row = row.copy()
        for col, converter in self.data_converters.items():
            new_row[col] = converter(row[col])
        return new_row

    def _create_new_strat_df(self, strat_name: str) -> pd.DataFrame:
        """
        Create an Empty Properly formatted Strategy Dataframe
        :param strat_name: Strategy Name
        :return: Pandas Dataframe of Strategy
        """
        self.trade_data[strat_name] = pd.DataFrame(data=DataTrades.strat_col_dtypes)
        self.trade_data[strat_name].set_index(keys=DataTrades.strat_indexes, inplace=True, drop=False, verify_integrity=True)
        return self.trade_data[strat_name]

    def dedupe(self, strat_name: str = None):
        """
        Remove any duplicate Rows based on "Entry time" and "Exit time"
        :param strat_name: Optional: Name of Strategy to dedupe. Default: is to dedupe ALL Strategy Dataframes
        """
        if strat_name is None:
            for name, strat_df in self.trade_data.items():
                self.trade_data[name] = self.get_strat_df(name).drop_duplicates(subset=DataTrades.strat_indexes, keep='last')
                self.trade_data[name].set_index(keys=DataTrades.strat_indexes, inplace=True, drop=False,
                                                      verify_integrity=False)
        else:
            strat_df = self.get_strat_df(strat_name)
            strat_df.drop_duplicates(subset=['Entry time', 'Exit time'], keep='last')
            self.trade_data[strat_name].set_index(keys=DataTrades.strat_indexes, inplace=True, drop=False,
                                            verify_integrity=False)

    def get_daily_returns(self, strat_name: str) -> pd.DataFrame:
        """
        Retrieve Daily Returns for a Strategy's transactions
        :param strat_name: Name of Strategy to look up
        :return: Pandas Datafrome grouped by a sum of the Daily Returns
        """
        df = self.get_strat_df(strat_name)
        return df.groupby(df['Exit time'].dt.date)['Profit'].sum()

    def get_strat_df(self, strat_name: str) -> pd.DataFrame:
        """
        Retrieve a Strategies Dataframe. If it's not been created yet, then return an empty properly formatted Strategy
        Dataframe
        :param strat_name: A String Name representing the Strategy's Name
        :return: A Strategy Dataframe
        """
        try:
            return self.trade_data[strat_name]
        except KeyError:
            logger.info(f"{strat_name} - Strategy does NOT exist in our database. Returning an Empty Strategy Dataframe")
            return self._create_new_strat_df(strat_name=strat_name)
