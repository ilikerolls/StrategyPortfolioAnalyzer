import pandas as pd

from src.utils import accounting_to_num, to_datetime


class SchemaDT:
    """Central Schema for DataTrades Dataframe that it Must Follow"""

    DT_INDEX_NAME: str = 'Exit time'
    DT_INDEX_DTYPE:str = 'datetime64[ns]'
    DT_INDEX_KEYS: list = ['Exit time', 'Entry time']
    # DT_INDEX: pd.DatetimeIndex = pd.DatetimeIndex(data=DT_INDEX_KEYS, dtype='datetime64[ns]', name=DT_INDEX_NAME)
    DT_INDEX = pd.Index(data=DT_INDEX_KEYS, name=DT_INDEX_NAME)

    DT_DATA_COL_DTYPES = {'Trade number': pd.Series(dtype='string'), 'Instrument': pd.Series(dtype='string'),
                        'Account': pd.Series(dtype='string'),
                        'Strategy': pd.Series(dtype='string'), 'Market pos.': pd.Series(dtype='string'),
                        'Qty': pd.Series(dtype='float'),
                        'Entry price': pd.Series(dtype='float'), 'Exit price': pd.Series(dtype='float'),
                        'Entry time': pd.Series(dtype='datetime64[ns]'),
                        'Exit time': pd.Series(dtype='datetime64[ns]'), 'Entry name': pd.Series(dtype='string'),
                        'Exit name': pd.Series(dtype='string'), 'Profit': pd.Series(dtype='float'),
                        'Cum. net profit': pd.Series(dtype='float'), 'Commission': pd.Series(dtype='float'),
                        'MAE': pd.Series(dtype='float'), 'MFE': pd.Series(dtype='float'), 'ETD': pd.Series(dtype='float'),
                        'Bars': pd.Series(dtype='int')}

    COL_NAMES_LIST: list = list(DT_DATA_COL_DTYPES.keys())

    # Data Converters
    DATA_CONVERTERS = {'Profit': accounting_to_num,'Cum. net profit': accounting_to_num,
                         "Commission": accounting_to_num,'ETD': accounting_to_num, 'MAE': accounting_to_num,'MFE': accounting_to_num, 'Entry time': to_datetime, 'Exit time': to_datetime}

    @staticmethod
    def format_row(row: dict) -> dict:
        """
        Convert a Dict of Data to proper formatting that our Dataframe Supports
        :param row: A dictionary of data including columns in strat_cols
        """
        formatted_row = {}
        for col, converter in SchemaDT.DATA_CONVERTERS.items():
            formatted_row[col] = converter(row[col])
        return formatted_row