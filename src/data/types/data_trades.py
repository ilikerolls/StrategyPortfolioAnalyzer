import pandas as pd

from src.conf_setup import logger
from src.data.analyzers.analyze_data_trades import AnalyzeDataTrades
from src.data.types.schema_data_trades import SchemaDT
from src.utils import Singleton


class DataTrades(AnalyzeDataTrades, metaclass=Singleton):
    """Holds each Strategies Trade Data"""

    trade_data: dict[str, pd.DataFrame] = {}

    def add_db_strat_trades(self, trades_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add a Strategy's trades Pandas Dataframe to the DataTrades Object
        :param trades_df: Pandas Dataframe with the Strategy's Trades
        :return: A Pandas Data from of the Added Strategy
        """
        strat_name = trades_df['Strategy'].iloc[0]
        self.trade_data[strat_name] = trades_df
        self.trade_data[strat_name].set_index(keys=SchemaDT.DT_INDEX_KEYS, inplace=True, drop=False, verify_integrity=False)
        # read_parquet doesn't return all the correct Data Types, but at least the important ones "Entry time" "Exit time"
        # TODO: 1 option if we decide we need it is to re-apply DataTrades.strat_col_dtypes to ALL columns, but so far we don't need it
        # Data Types:\n{self.trade_data[strat_name].dtypes}
        return self.trade_data[strat_name]

    def add_trade_data(self, row: dict):
        """
        Add a trade to a Strategy from a CSV file. NOTE: We need to do 1 line at a time, because a .csv file may contain
        multiple Strategy names in it.
        :param row: A Dictionary Row with same keys as self.strat_cols(Columns)
        """
        formatted_row: dict = SchemaDT.format_row(row=row)
        try:
            strat_name = formatted_row['Strategy']
            # Creates a new Dataframe for the Strategy if one doesn't already Exist
            strat_df = self.get_strat_df(strat_name=strat_name)
            row_df = pd.DataFrame(data=[formatted_row.values()], columns=SchemaDT.COL_NAMES_LIST)
            self.trade_data[strat_name] = pd.concat([strat_df, row_df])
        except KeyError as ke:
            logger.error(f"Improperly formatted row. Couldn't find 'Strategy' column in .csv.\nFormat should be: "
                         f"{SchemaDT.COL_NAMES_LIST}\nrow: {row}\nformatted row: {formatted_row}\nException: {ke}")

    def _create_new_strat_df(self, strat_name: str) -> pd.DataFrame:
        """
        Create an Empty Properly formatted Strategy Dataframe
        :param strat_name: Strategy Name
        :return: Pandas Dataframe of Strategy
        """
        self.trade_data[strat_name] = pd.DataFrame(data=SchemaDT.DT_DATA_COL_DTYPES)
        self.trade_data[strat_name].set_index(keys=SchemaDT.DT_INDEX_KEYS, inplace=True, drop=False, verify_integrity=False)
        return self.trade_data[strat_name]

    def dedupe(self, strat_name: str = None):
        """
        Remove any duplicate Rows based on "Entry time" and "Exit time"
        :param strat_name: Optional: Name of Strategy to dedupe. Default: is to dedupe ALL Strategy Dataframes
        """
        if strat_name is None:
            for name, strat_df in self.trade_data.items():
                self.get_strat_df(name).drop_duplicates(subset=SchemaDT.DT_INDEX_KEYS, keep='last', inplace=True)
                self.trade_data[name].set_index(keys=SchemaDT.DT_INDEX_KEYS, inplace=True, drop=False,
                                                      verify_integrity=False)
        else:
            self.get_strat_df(strat_name).drop_duplicates(subset=['Entry time', 'Exit time'], keep='last', inplace=True)
            self.trade_data[strat_name].set_index(keys=SchemaDT.DT_INDEX_KEYS, inplace=True, drop=False,
                                            verify_integrity=False)

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

    def strats_to_list(self) -> list:
        """
        :return: A list of Loaded Strategies
        """
        return list(self.trade_data.keys())
